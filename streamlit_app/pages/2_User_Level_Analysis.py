import streamlit as st
import streamlit_analytics
import numpy as np
from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css
from streamlit_extras.buy_me_a_coffee import button
from utils.graphs_utils import generate_message_responses_flow
from PIL import Image
import pandas as pd
import emoji
from utils.text_utils import get_emojis_bow

USER_IMAGE = Image.open("streamlit_app/streamlit/styles/logos/user_logo.jpg")

def human_format(num, round_to=0):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return '{:.{}f}{}'.format(num, round_to, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


def add_metric_black_b():
    css_body_container = f'''
             <style>
                 [data-testid="stVerticalBlock"] div:nth-of-type(1)
                 [data-testid="stVerticalBlock"] {{background-color:rgba(11,20,26)}}
             </style>
             '''

    st.markdown(css_body_container, unsafe_allow_html=True)


def center_photo():
    css_center = """<style>body {
        background-color: #eee;
    }
    
    .fullScreenFrame > div {
        display: flex;
        justify-content: center;
    }</style>"""
    st.markdown(css_center, unsafe_allow_html=True)


def calc_n_user_per_row(top_n_users):

    if top_n_users % 2 == 0:
        users_per_row = top_n_users / 2
        output = [users_per_row, users_per_row]

    else:
        output = [np.floor(top_n_users / 2.0), np.ceil(top_n_users / 2.0)]

    if output[0] == 0:
        output[0] = output[1]
        output[1] = 0
    return output


def get_users_metrics(df, top_n):

    agg_df = df.groupby('username', as_index=False).agg(n_days=('date', 'nunique'),
                                n_messages=('username', 'count'),
                                n_conversation=('conversation_id', 'nunique'),
                                n_words=('text_length', 'sum'),
                                n_media=('is_media', 'sum'))

    emoji_bow = get_emojis_bow(df)
    top_freq_emoji = pd.DataFrame(emoji_bow.drop([' '], axis=1).idxmax(axis=1)).reset_index()\
        .rename(columns={0: 'top_freq_emoji'})

    return agg_df.merge(top_freq_emoji, on='username', how='left')\
        .sort_values('n_messages', ascending=False).reset_index(drop=True)[0:top_n]


def assign_metrics(col, image, user_info,language, add_seperator=True):

    n_mes_lang_dict = {'en': "N Messages", 'he': 'סה"כ הודעות'}
    n_wor_lang_dict = {'en': "N Words", 'he': 'סה"כ מילים'}
    n_days_lang_dict = {'en': "N Active Days", 'he': 'סה"כ ימים פעילים'}
    n_conv_lang_dict = {'en': "N Conversation", 'he': 'סה"כ שיחות'}
    n_media_lang_dict = {'en': "N Media", 'he': 'תמונת/סרטונים'}
    emoji_lang_dict = {'en': "Top Emoji", 'he': "אימוג'י שכיח"}

    col.image(image, caption=user_info.username, width=100)
    col1, col2 = st.columns((2, 2))
    col1.metric(n_mes_lang_dict[language], human_format(user_info.n_messages))
    col1.metric(n_wor_lang_dict[language], human_format(user_info.n_words))
    col2.metric(n_days_lang_dict[language], f"{user_info.n_days:,}")
    col2.metric(n_conv_lang_dict[language], human_format(user_info.n_conversation))

    col1.metric(n_media_lang_dict[language], human_format(user_info.n_media))
    if emoji.is_emoji(user_info.top_freq_emoji):
        col2.metric(emoji_lang_dict[language], emoji.emojize(emoji.demojize(user_info.top_freq_emoji)))
    else:
        col2.metric(emoji_lang_dict[language], 'No Emoji')
    if add_seperator:
        st.write('---------------')


def main():

    st.set_page_config(layout="wide", page_title="User Level Analysis", page_icon="👫")
    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:

        filtered_df, min_date, max_date, language = add_filters()

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))

        header_text = {'en': 'User Level Analysis', 'he': 'ניתוח משתמשים'}
        st.subheader(header_text[language])

        top_n_users = min(filtered_df['username'].nunique(), 8)

        metrics_df = get_users_metrics(filtered_df, top_n_users)

        row_a_n_users, row_b_n_users = calc_n_user_per_row(top_n_users)

        row_a = st.columns(np.array(int(row_a_n_users) * [10]))

        for col, user_info in zip(row_a, metrics_df[:int(row_a_n_users)].to_records()):

            with col:
                assign_metrics(col, USER_IMAGE, user_info, language=language)

        if row_b_n_users != 0:

            for col, user_info in zip(row_a, metrics_df[int(row_b_n_users):].to_records()):
                with col:
                    assign_metrics(col, USER_IMAGE, user_info, language=language,add_seperator=False)

        add_metric_black_b()

        # st.write(get_users_metrics(filtered_df, top_n_users))

        # st.markdown(css_body_container, unsafe_allow_html=True)

        # conversation = st.sidebar.multiselect("Conversation", list(filtered_df['conversation_id'].unique()))
        #
        # st.write(filtered_df[filtered_df['conversation_id'].isin(conversation)])


# Run the app
if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    button(username="bigalon1991", width=221)
    streamlit_analytics.stop_tracking()
