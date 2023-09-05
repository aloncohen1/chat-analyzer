import emoji
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

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