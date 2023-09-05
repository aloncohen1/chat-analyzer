import json
import requests
import pandas as pd
from googletrans import Translator

API_TOKEN='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'
API_URL = "https://api-inference.huggingface.co/models/philschmid/bart-large-cnn-samsum"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def preprocess_text(df, in_nusers=1, min_n_messages=3):
    df['text'] = df['username'] + ': ' + df['message'].astype(str).str.replace('<Media omitted>', '<sent a photo>')
    text_df = df.groupby('conversation_id', as_index=False) \
        .agg({"text": '\n'.join,
              'username': 'nunique',
              'conversation_id': 'count'}) \
        .rename(columns={'username': 'n_users',
                         'conversation_id': 'n_messages'})

    text_df = text_df[(text_df['n_users'] > in_nusers) &
                      (text_df['n_messages'] > min_n_messages)]
    return text_df


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


def sum_text(text_list):

    trans_text = run_trans(text_list)

    sum_texts = query_hg({'inputs': [i['translation'] for i in trans_text], 'wait_for_model': True})

    top_src = pd.DataFrame(trans_text)['src'].value_counts().index[0]
    if top_src != 'en':

        back_trans = run_trans([i.get('summary_text') for i in sum_texts], dest=top_src)
        final_text = [i['translation'] for i in back_trans]
    else:
        final_text = [i.get('summary_text') for i in sum_texts]

    return final_text
