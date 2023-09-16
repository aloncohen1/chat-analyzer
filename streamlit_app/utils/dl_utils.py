import json
import re
import requests
import pandas as pd
from googletrans import Translator
import streamlit as st

API_TOKEN ='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'
API_URL = "https://api-inference.huggingface.co/models/philschmid/bart-large-cnn-samsum"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def wake_up_model(run=False):
    if run:
      data = json.dumps({'inputs': 'wake up model',
                        'wait_for_model': True})
      requests.request("POST", API_URL, headers=headers, data=data)


def preprc_text_for_sum(row):
    row.message = str(row.message)
    row.message = re.sub(r"http\S+", "<link>", row.message).lower()
    row.message = row.message.replace('<media omitted>', '<here is a photo>')

    return row.username + ': ' + row.message

def get_conv_df(df, min_users=2, min_messages=4, min_length=8):

    df['preproc_text'] = df.apply(lambda x: preprc_text_for_sum(x), axis=1)

    conv_df = df.groupby('conversation_id') \
        .agg({"preproc_text": '\n'.join,
              'username': 'nunique',
              'timestamp': 'count',
              'is_media': 'sum',
              'text_length': 'sum',
              'date': 'min'}) \
        .rename(columns={'username': 'n_users',
                         'timestamp': 'n_messages'})
    conv_df = conv_df[(conv_df['n_users'] >= min_users) &
                      (conv_df['n_messages'] >= min_messages) &
                      (conv_df['text_length'] >= min_length) &
                      (conv_df['n_messages'] > conv_df['is_media'])].reset_index()
    return conv_df


def query_hg(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))


def run_trans(text_list, dest='en'):
    translator = Translator()
    translations = translator.translate(text_list, dest=dest)

    results_list = []
    for translation in translations:
        try:
            results_list.append({'src': translation.src, 'translation': translation.text})
        except Exception:
            results_list.append({'src': None, 'translation': None})

    return results_list

@st.cache_data
def get_sum_text(text_list):

    trans_text = run_trans(text_list)

    sum_texts = query_hg({'inputs': [i['translation'] for i in trans_text], 'wait_for_model': True})

    top_src = pd.DataFrame(trans_text)['src'].value_counts().index[0]
    if top_src != 'en':

        back_trans = run_trans([i.get('summary_text') for i in sum_texts], dest=top_src)
        final_text = [i['translation'] for i in back_trans]
    else:
        final_text = [i.get('summary_text') for i in sum_texts]

    return final_text


