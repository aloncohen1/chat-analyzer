import emoji
import numpy as np
import scipy.sparse as sp
from scipy.sparse import csr_matrix
import streamlit as st
from googletrans import Translator
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer

import pandas as pd
import nltk

if not st.session_state.get('bcp47_downloaded'):
    nltk.download('bcp47')
    st.session_state['bcp47_downloaded'] = True

if not st.session_state.get('stopwords_downloaded'):
    nltk.download('stopwords')
    st.session_state['stopwords_downloaded'] = True

if not st.session_state.get('wordnet_downloaded'):
    nltk.download('wordnet')
    st.session_state['wordnet_downloaded'] = True


from nltk.stem.porter import PorterStemmer
from nltk import WordNetLemmatizer
import nltk.langnames as lgn
from nltk.corpus import stopwords
import gensim
import re
import time

from sklearn.preprocessing import normalize

def stream_data(text,latncy=0.04):
    for word in text.split():
        yield word + " "
        time.sleep(latncy)


def human_format(num, pct=True):
    if pct:
        return "{0:.0f}%".format(num * 100)
    else:
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num = round(num / 1000.0, 0)
        return '{:.{}f}{}'.format(num, 0, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def get_users_emoji_df(df, method='top_freq'):
    if method=='top_freq':
        df['emojis_list'] = df['message'].apply(lambda x: [i['emoji'] for i in emoji.emoji_list(str(x))])
    else:
        df['emojis_list'] = df['message'].apply(lambda x: [i for i in emoji.distinct_emoji_list(str(x))])

    emoji_df = df[df['emojis_list'].apply(len) > 0].groupby('username',as_index=False).agg({'emojis_list': 'sum'})
    return emoji_df


def get_top_emojis(df, method='Most Frequent'):

    emoji_df = get_users_emoji_df(df, method)

    def dummy(doc):
        return doc

    vectorizer = CountVectorizer(tokenizer=dummy,preprocessor=dummy)
    X = vectorizer.fit_transform(emoji_df['emojis_list'])
    emojies = vectorizer.get_feature_names_out()

    if method == 'Most Frequent':

        bow_df = pd.DataFrame(X.toarray(), columns=emojies, index=emoji_df['username'])

        top_fre_emoji = pd.DataFrame(bow_df.idxmax(axis=1)).reset_index() \
            .rename(columns={0: 'top_freq_emoji'})
    else:

        ctfidf = CTFIDFVectorizer().fit_transform(X, n_samples=len(emoji_df)).toarray()
        words_per_class_min = {user_name: [emojies[index] for index in ctfidf[label].argsort()[-1:]]
                               for label, user_name in zip(emoji_df.username.index, emoji_df.username)}

        return pd.DataFrame(words_per_class_min).T.reset_index()\
            .rename(columns={0: 'top_freq_emoji','index':'username'})

    return top_fre_emoji


def detect_lang(df, n_sample=30, min_text_length=10):

    sample_df = df[df['text_length'] > min_text_length].sample(n_sample)
    translator = Translator()

    lang_src = translator.detect(sample_df['message'].astype(str).to_list())

    top_lng = pd.DataFrame([i.lang for i in lang_src],
                           columns=['lang'])['lang'].value_counts().index[0]

    st.session_state['lang'] = top_lng




def get_lang_stop_words(df):

    if not st.session_state.get('lang'):
        detect_lang(df)
    top_lng_name = lgn.langname(st.session_state['lang'])
    if top_lng_name:
        top_lng_name = top_lng_name.lower()
        if top_lng_name in stopwords.fileids():
            stop_words = stopwords.words(top_lng_name)
        else:
            stop_words = stopwords.words('english')
    else:
        stop_words = stopwords.words('english')

    return stop_words


def get_users_top_worlds(df, n_users=10, top_words=5):

    if not st.session_state.get('lang'):
        detect_lang(df)
    lang = lgn.langname(st.session_state['lang'])
    stop_words = get_lang_stop_words(df)

    if lang == "hebrew":
        stop_words +=[f'{i}ו' for i in stop_words]
        stop_words += [f'{i}מ' for i in stop_words]
        stop_words += [f'{i}ה' for i in stop_words]

    df['clean_text'] = df['message'].apply(lambda x: clean_text(x, lang))

    users = df['username'].value_counts()[: min(df['username'].nunique(),n_users)].index

    users_text = df[(df['is_media']==False) &
                    (df['username'].isin(users))]\
        .groupby(['username'], as_index=False).agg({'clean_text': ' '.join})

    users_top_worlds = run_ctfidf(users_text, stop_words, top_words)

    return users_top_worlds.T


def clean_text(text, lang='english', ):

    text_list = gensim.utils.simple_preprocess(text)

    if lang == "english":
        stemmer = PorterStemmer()
        result = []
        for token in text_list:
            result.append(stemmer.stem(WordNetLemmatizer().lemmatize(token, pos='v')))
        text_list = result

    return ' '.join(text_list)


class CTFIDFVectorizer(TfidfTransformer):
    def __init__(self, *args, **kwargs):
        super(CTFIDFVectorizer, self).__init__(*args, **kwargs)

    def fit(self, X: sp.csr_matrix, n_samples: int):
        """Learn the idf vector (global term weights) """
        _, n_features = X.shape
        df = np.squeeze(np.asarray(X.sum(axis=0)))
        idf = np.log(n_samples / df)
        self._idf_diag = sp.diags(idf, offsets=0,
                                  shape=(n_features, n_features),
                                  format='csr',
                                  dtype=np.float64)
        return self

    def transform(self, X: sp.csr_matrix) -> sp.csr_matrix:
        """Transform a count-based matrix to c-TF-IDF """
        X = X * self._idf_diag
        X = normalize(X, axis=1, norm='l1', copy=False)
        return X


def run_ctfidf(users_text, stop_words, top_words=5):

    n_users = users_text['username'].nunique()

    count_vectorizer = CountVectorizer(stop_words=stop_words,
                                       ngram_range=(1, 2),
                                       min_df=max(1, n_users) if n_users<=3 else 2).fit(users_text.clean_text)
    count = count_vectorizer.transform(users_text.clean_text)
    words = count_vectorizer.get_feature_names_out()

    nnz_inds = count.nonzero()
    keep = np.where(count.data > 2)[0]
    n_keep = len(keep)
    count = csr_matrix((np.ones(n_keep), (nnz_inds[0][keep], nnz_inds[1][keep])), shape=count.shape)

    # Extract top 10 words per class
    ctfidf = CTFIDFVectorizer().fit_transform(count, n_samples=len(users_text)).toarray()
    words_per_class_min = {user_name: [words[index] for index in ctfidf[label].argsort()[-top_words:]]
                           for label, user_name in zip(users_text.username.index, users_text.username)}

    return pd.DataFrame(words_per_class_min)



# def run_emoji_ctfidf(users_text, stop_words, top_words=5):
#
#
#
#     count_vectorizer = CountVectorizer(stop_words=stop_words,
#                                        ngram_range=(1, 2),
#                                        min_df=max(1, n_users) if n_users<=3 else 2).fit(users_text.clean_text)
#     count = count_vectorizer.transform(users_text.clean_text)
#     words = count_vectorizer.get_feature_names_out()
#
#     nnz_inds = count.nonzero()
#     keep = np.where(count.data > 2)[0]
#     n_keep = len(keep)
#     count = csr_matrix((np.ones(n_keep), (nnz_inds[0][keep], nnz_inds[1][keep])), shape=count.shape)
#
#     # Extract top 10 words per class
#     ctfidf = CTFIDFVectorizer().fit_transform(count, n_samples=len(users_text)).toarray()
#     words_per_class_min = {user_name: [words[index] for index in ctfidf[label].argsort()[-top_words:]]
#                            for label, user_name in zip(users_text.username.index, users_text.username)}
#
#     return pd.DataFrame(words_per_class_min)

