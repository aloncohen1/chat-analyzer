import pandas as pd
import streamlit as st
import streamlit_analytics
import numpy as np
from app_utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, linkedin_link, \
    form_link, buy_me_a_coffee_link
from streamlit_extras.buy_me_a_coffee import button
from PIL import Image
import emoji

from app_utils.graphs_utils import plotly_wordcloud
from app_utils.text_utils import get_top_emojis, human_format, get_top_worlds

USER_IMAGE = Image.open("add_ons/styles/logos/user_logo.jpg")





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


def get_users_metrics(df, top_n,emoji_method, min_date, max_date):

    agg_df = df.groupby('username', as_index=False).agg(n_days=('date', 'nunique'),
                                n_messages=('username', 'count'),
                                n_conversation=('conversation_id', 'nunique'),
                                n_words=('text_length', 'sum'),
                                n_media=('is_media', 'sum'))

    totals_df = df.agg(n_days=('date', 'nunique'),
                       n_messages=('username', 'count'),
                       n_conversation=('conversation_id', 'nunique'),
                       n_words=('text_length', 'sum'),
                       n_media=('is_media', 'sum')).max(axis=1)

    top_emoji = get_top_emojis(st.session_state['data'][st.session_state['data']['date'].between(min_date, max_date)],
                               emoji_method)

    agg_df = agg_df.merge(top_emoji, on='username', how='left') \
        .sort_values('n_messages', ascending=False).reset_index(drop=True)[0:top_n]

    return agg_df, totals_df


def assign_metrics(col, totals_df, image, user_info, language, add_seperator=True, pct=True,add_bot=True):

    sign = {'en': '%' if pct else 'N', 'he': '%' if pct else 'סה"כ'}

    n_mes_lang_dict = {'en': f"{sign[language]} Messages", 'he': f'{sign[language]} הודעות'}
    n_wor_lang_dict = {'en': f"{sign[language]} Words", 'he': f'{sign[language]} מילים'}
    n_days_lang_dict = {'en': f"{sign[language]} Active Days", 'he': f'{sign[language]} ימים פעילים'}
    n_conv_lang_dict = {'en': f"{sign[language]} Conversation", 'he': f'{sign[language]} שיחות'}
    n_media_lang_dict = {'en': f"{sign[language]} Media", 'he': f'תמונת/סרטונים'}
    emoji_lang_dict = {'en': "Top Emoji", 'he': "אימוג'י"}
    if not col:
        col = st.columns((1, 0.001))
    col.image(image, caption=user_info.username, width=100)
    col1, col2 = st.columns((2, 2))
    col1.metric(n_mes_lang_dict[language], human_format(user_info.n_messages / (totals_df.n_messages if pct else 1), pct))
    col1.metric(n_wor_lang_dict[language], human_format(user_info.n_words/ (totals_df.n_words if pct else 1), pct))
    col2.metric(n_days_lang_dict[language], human_format(user_info.n_days / (totals_df.n_days if pct else 1), pct))
    col2.metric(n_conv_lang_dict[language], human_format(user_info.n_conversation/ (totals_df.n_conversation if pct else 1), pct))

    col1.metric(n_media_lang_dict[language], human_format(user_info.n_media/ (totals_df.n_media if pct else 1), pct))
    if emoji.is_emoji(user_info.top_freq_emoji):
        col2.metric(emoji_lang_dict[language], emoji.emojize(emoji.demojize(user_info.top_freq_emoji)))
    else:
        col2.metric(emoji_lang_dict[language], 'No Emoji')
    bot = st.button('Show me More', key=user_info.username) if add_bot else None
    if add_seperator:
        st.divider()

    return bot


def gen_landing_page(filtered_df, language, min_date, max_date):

    header_text = {'en': 'User Level Analysis', 'he': 'ניתוח משתמשים'}
    st.subheader(header_text[language])
    top_col, _ = st.columns((1000, 0.1))
    with top_col:
        pct_lang_dict = {'en': "Show Percentages", "he": 'הצג אחוזים'}

        method_lang_dict = {'en': {"Most Associated": "Most Associated",
                                   "Most Frequent": "Most Frequent"},
                            "he": {"המזוהה ביותר": "Most Associated",
                                   "התדיר ביותר": "Most Frequent"}}

        pct = st.checkbox(pct_lang_dict[language])
        emohi_picker_lang_dict = {'en': "Top Emoji Method", 'he': "איזה אימוג'י"}
        emoji_method = st.radio(emohi_picker_lang_dict[language], list(method_lang_dict[language].keys()))

        emoji_method = method_lang_dict[language][emoji_method]

    top_n_users = min(filtered_df['username'].nunique(), 8)

    metrics_df, totals_df = get_users_metrics(filtered_df, top_n_users, emoji_method, min_date, max_date)

    # st.write(metrics_df)

    row_a_n_users, row_b_n_users = calc_n_user_per_row(top_n_users)

    row_a = st.columns(np.array(int(row_a_n_users) * [10]))

    bot_list = []

    for col, user_info in zip(row_a, metrics_df[:int(row_a_n_users)].to_records()):
        with col:
            bot = assign_metrics(col, totals_df, USER_IMAGE, user_info, language=language, pct=pct)
            bot_list.append({'username': user_info.username, 'gen_report': bot, "user_info":user_info})

    if row_b_n_users != 0:

        for col, user_info in zip(row_a, metrics_df[int(row_b_n_users):].to_records()):
            with col:
                bot = assign_metrics(col, totals_df, USER_IMAGE, user_info, language=language, add_seperator=False,
                                     pct=pct)
                bot_list.append({'username': user_info.username, 'gen_report': bot, "user_info":user_info})

    add_metric_black_b()

    return totals_df, bot_list

def callback():
    pass

@st.dialog('User Analysis',width='large')
def gen_user_report(bot_list, totals_df, language, users_words_df):
    selected_user = [i for i in bot_list if i['gen_report'] is True]
    # st.write([i for i in bot_list if i['gen_report'] is True])
    my_col, _ = st.columns((1, 0.0001))
    with my_col:
        assign_metrics(my_col, totals_df, USER_IMAGE, selected_user[0]['user_info'],
                       language=language, add_seperator=False, pct=True, add_bot=False)

        user_words_df = users_words_df[users_words_df['username'] == selected_user[0]['username']]
        user_words_df['rank'] = user_words_df['rank'] / user_words_df['rank'].sum()

        wordcloud_fig = plotly_wordcloud(user_words_df.set_index('term')['rank'].to_dict())

        selected_words = st.plotly_chart(wordcloud_fig, use_container_width=True, on_select='rerun', selection_mode='box',
                                         key='my_chart')
        st.write(selected_words)

def get_user_terms_texts(df):
    pass

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

        users_words_df = get_top_worlds(filtered_df)

        user_level_landing_page = st.empty()
        with user_level_landing_page.container():
            # st.write('naive')
            # st.write(users_words_df)

            totals_df, bot_list = gen_landing_page(filtered_df, language, min_date, max_date)


        if any([i['gen_report'] for i in bot_list]):

            gen_user_report(bot_list, totals_df, language, users_words_df)




# Run the app
if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    # button(username="bigalon1991", width=221)
    linkedin_link()
    form_link()
    buy_me_a_coffee_link()
    streamlit_analytics.stop_tracking(unsafe_password=st.secrets["tracking_pass"])
