import emoji
import pandas as pd
from googletrans import Translator
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import nltk



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
    return top_lng



def get_lang_stop_words(df):
    
    nltk.download('bcp47')
    nltk.download('stopwords')
    import nltk.langnames as lgn
    from nltk.corpus import stopwords

    top_lng_code_name = detect_lang(df)
    top_lng_name = lgn.langname(top_lng_code_name)
    if top_lng_name:
        top_lng_name = top_lng_name.lower()
        if top_lng_name in stopwords.fileids():
            stop_words = stopwords.words(top_lng_name)
        else:
            stop_words = stopwords.words('english')
    else:
        stop_words = stopwords.words('english')

    return stop_words


