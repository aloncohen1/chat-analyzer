from time import sleep
import pandas as pd
import requests
import streamlit_analytics
from streamlit_extras.switch_page_button import switch_page
from whatstk.whatsapp.parser import _df_from_str

import streamlit as st
# from utils.whatspp_utils import _df_from_str

from utils.general_utils import add_metadata_to_df, set_background, add_logo, generate_synthetic_locations
from utils.telegram_utils import parse_telegram_html

# TEST_DATA_URL = "https://raw.githubusercontent.com/tusharnankani/whatsapp-chat-data-analysis/main/whatsapp-chat-data.txt"
CHAT_EXAMPLE_PATH = 'example_chat.txt'


def load_test_data():
    progress_bar = st.progress(0, text="Loading...")
    # data = requests.get(TEST_DATA_URL).text
    with open(CHAT_EXAMPLE_PATH) as f:
        data = f.read()
    df = _df_from_str(data)
    df = generate_synthetic_locations(df)
    df = add_metadata_to_df(df).sort_values('timestamp').reset_index(drop=True)
    st.session_state['data'] = df
    st.session_state['lang'] = None
    st.session_state['file_name'] = 'Chat for Example'
    progress_bar.progress(100)


def load_data(files):
    progress_bar = st.progress(0, text="Uploading...")
    df_list = []
    for index, file in enumerate(files):
        if file.name.endswith('.txt'):
            df_list.append(_df_from_str(file.read().decode()))
            st.session_state['file_name'] = file.name.replace('.txt', '')\
                .replace('WhatsApp Chat with', '').replace('_','')

        elif file.name.endswith('.html'):
            group_name, group_df = parse_telegram_html(file.read().decode())
            st.session_state['file_name'] = group_name
            df_list.append(group_df)

        progress_bar.progress(((index + 1) / len(files)), text="Uploading...")
    final_df = add_metadata_to_df(pd.concat(df_list, ignore_index=True)).sort_values('timestamp')
    st.session_state['data'] = final_df
    st.session_state['lang'] = None

    progress_bar.progress(100)



def main():

    st.set_page_config(layout="wide", page_title="Hello", page_icon="👋")

    set_background()

    add_logo()
    st.title("Chat Group Analyzer")

    home_holder = st.empty()
    home_holder.header("Upload Data")
    home_holder.subheader("Supports Whatsapp (.txt) / Telegram (.html)")

    uploading_holder = st.empty()
    uploaded_file = uploading_holder.file_uploader("Choose a TXT / HTML file/s", type=["txt", "html"],
                                                   accept_multiple_files=True)

    test_file_holder = st.empty()
    load_test = test_file_holder.button("Load Chat Example File", type="primary")

    how_to_text_holder = st.empty()
    how_to_pic_holder = st.empty()

    with how_to_text_holder:
        col0, col1 = st.columns((2, 1))

        col0.subheader("How to export WhatsApp chat - [Click Here](https://faq.whatsapp.com/1180414079177245)")
        col1.subheader("How to export Telegram chat - [Click Here](https://telegram.org/blog/export-and-more)")

    with how_to_pic_holder:

        col2, col3 = st.columns((2, 1))

        col2.markdown('[![Foo](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/240px-WhatsApp.svg.png)](https://faq.whatsapp.com/1180414079177245/)')
        col3.markdown('[![Foo](https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Telegram_2019_Logo.svg/242px-Telegram_2019_Logo.svg.png)](https://telegram.org/blog/export-and-more)')

    if uploaded_file:
        uploading_holder.empty()
        test_file_holder.empty()
        home_holder.empty()
        how_to_text_holder.empty()
        how_to_pic_holder.empty()
        load_data(uploaded_file)
        switch_page("basic statistics")
        st.write("Chat Uploaded Successfully!")
        sleep(2)

    elif load_test:
        test_file_holder.empty()
        uploading_holder.empty()
        home_holder.empty()
        how_to_text_holder.empty()
        how_to_pic_holder.empty()
        load_test_data()
        test_file_holder.empty()
        sleep(2)
        st.write("Chat Uploaded Successfully!")
        switch_page("basic statistics")


if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    streamlit_analytics.stop_tracking()
