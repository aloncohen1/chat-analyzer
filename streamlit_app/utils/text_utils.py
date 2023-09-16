import emoji
import numpy as np
import scipy.sparse as sp
from scipy.sparse import csr_matrix
import streamlit
from googletrans import Translator
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

import pandas as pd
import nltk
from nltk.stem.porter import PorterStemmer
from nltk import WordNetLemmatizer
nltk.download('bcp47')
nltk.download('stopwords')
import nltk.langnames as lgn
from nltk.corpus import stopwords
import gensim
import re

from sklearn.preprocessing import normalize


def get_users_emoji_df(df):
    df['emojis'] = df['message'].apply(lambda x: ''.join([i['emoji'] for i in emoji.emoji_list(str(x))]))
    df['distinct_emojis'] = df['message'].apply(lambda x: ''.join(emoji.distinct_emoji_list(str(x))))

    users_emoji_df = df[df['distinct_emojis'] != ''].groupby('username', as_index=False).agg({'emojis': 'sum'})
    return users_emoji_df


def get_emojis_bow(df):

    users_emoji_df = get_users_emoji_df(df)

    vectorizer = CountVectorizer(token_pattern=r'[^\s]+', analyzer='char_wb')
    X = vectorizer.fit_transform(users_emoji_df['emojis'])
    bow_df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out(), index=users_emoji_df['username'])
    # bow_df.head()
    # pd.DataFrame(bow_df.drop([' '], axis=1).idxmax(axis=1)).reset_index().rename(columns={0: 'top_freq_emoji'})

    return bow_df


# def get_languages_df(df):
#     lan = Detector(df['message'].astype(str).sum()).languages
#     return pd.DataFrame(lan)

def detect_lang(df, n_sample=30, min_text_length=10):

    sample_df = df[df['text_length'] > min_text_length].sample(n_sample)
    translator = Translator()

    lang_src = translator.detect(sample_df['message'].astype(str).to_list())

    top_lng = pd.DataFrame([i.lang for i in lang_src],
                           columns=['lang'])['lang'].value_counts().index[0]

    streamlit.session_state['lang'] = top_lng




def get_lang_stop_words(df):

    if not streamlit.session_state.get('lang'):
        detect_lang(df)
    top_lng_name = lgn.langname(streamlit.session_state['lang'])
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

    if not streamlit.session_state.get('lang'):
        detect_lang(df)
    lang = lgn.langname(streamlit.session_state['lang'])
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


def clean_text(text, lang):
    text = re.sub(r"http\S+", "", text).lower()
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