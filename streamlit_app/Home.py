from time import sleep
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

import streamlit as st
from whatstk.whatsapp.parser import _df_from_str
from utils.general_utils import add_timestamps_df, set_background, add_logo
from utils.telegram_utils import parse_telegram_html


#
# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

def load_data(files):
    progress_bar = st.progress(0, text="Uploading...")
    df_list = []
    for index, file in enumerate(files):
        if file.name.endswith('.txt'):
            df_list.append(_df_from_str(file.read().decode()))
        elif file.name.endswith('.html'):
            df_list.append(parse_telegram_html(file.read().decode()))

        progress_bar.progress(((index + 1) / len(files)), text="Uploading...")
    final_df = add_timestamps_df(pd.concat(df_list)).sort_values('timestamp')
    st.session_state['data'] = final_df

    progress_bar.progress(100)



def main():
    set_background()

    add_logo()
    st.title("Chat Group Analyzer")

    test_holder = st.empty()
    test_holder.header("Upload Data")
    test_holder.write("Supports Whatsapp (.txt) / Telegram (.html)")

    uploading_holder = st.empty()
    uploaded_file = uploading_holder.file_uploader("Choose a TXT / HTML file/s", type=["txt", "html"],
                                                   accept_multiple_files=True)

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

        load_data(uploaded_file)
        uploading_holder.empty()
        test_holder.empty()
        how_to_text_holder.empty()
        how_to_pic_holder.empty()
        st.write("Chat Uploaded Successfully!")
        # st.header("Chat Uploaded Successfully!")
        sleep(2)
        switch_page("basic statistics")



if __name__ == "__main__":
    main()
