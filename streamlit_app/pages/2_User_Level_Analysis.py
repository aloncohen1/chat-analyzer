import streamlit as st
import numpy as np
from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css
from utils.graphs_utils import generate_message_responses_flow
from PIL import Image
import pandas as pd

from utils.text_utils import get_emojis_bow


def add_metric_black_b():
    css_body_container = f'''
             <style>
                 [data-testid="stVerticalBlock"] div:nth-of-type(1)
                 [data-testid="stVerticalBlock"] {{background-color:rgba(11,20,26,0.6)}}
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
                                n_words=('text_length', 'sum'))

    emoji_bow = get_emojis_bow(df)
    top_freq_eemoji = pd.DataFrame(emoji_bow.drop([' '], axis=1).idxmax(axis=1)).reset_index()\
        .rename(columns={0: 'top_freq_emoji'})

    return agg_df.merge(top_freq_eemoji, on='username', how='left')\
        .sort_values('n_messages', ascending=False).reset_index(drop=True)[0:top_n]

def main():

    st.set_page_config(layout="wide")
    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        image = Image.open("streamlit_app/streamlit/styles/logos/user_logo.jpg")

        filtered_df, min_date, max_date = add_filters()

        top_n_users = min(filtered_df['username'].nunique(), 9)

        metrics_df = get_users_metrics(filtered_df,top_n_users)

        row_a_n_users, row_b_n_users = calc_n_user_per_row(top_n_users)

        row_a = st.columns(np.array(int(row_a_n_users) * [10]))

        for col, user_info in zip(row_a, metrics_df[:int(row_a_n_users)].to_records()):
            with col:
                col.image(image, caption=user_info.username, width=100)
                col1, col2 = st.columns((2,2))
                col1.metric('n messeges', f"{user_info.n_messages:,}")
                col1.metric('n words', f"{user_info.n_words:,}")
                col2.metric('n days', f"{user_info.n_days:,}")
                col2.metric('n conversation', f"{user_info.n_conversation:,}")
                col1.metric('most used emoji', user_info.top_freq_emoji)

        if row_b_n_users != 0:
            for col, user_info in zip(row_a, metrics_df[int(row_b_n_users):].to_records()):
                with col:
                    col.image(image, caption=user_info.username, width=100)
                    col1, col2 = st.columns((2, 2))
                    col1.metric('n messeges', f"{user_info.n_messages:,}")
                    col1.metric('n words', f"{user_info.n_words:,}")
                    col2.metric('n days', f"{user_info.n_days:,}")
                    col2.metric('n conversation', f"{user_info.n_conversation:,}")
                    col1.metric('most used emoji', user_info.top_freq_emoji)

        add_metric_black_b()

        st.write(get_users_metrics(filtered_df,top_n_users))

        # st.markdown(css_body_container, unsafe_allow_html=True)

        # conversation = st.sidebar.multiselect("Conversation", list(filtered_df['conversation_id'].unique()))
        #
        # st.write(filtered_df[filtered_df['conversation_id'].isin(conversation)])


# Run the app
if __name__ == "__main__":
    main()
