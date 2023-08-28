from streamlit_extras.switch_page_button import switch_page

import streamlit as st
from whatstk.whatsapp.parser import _df_from_str
from utils.general_utils import add_timestamps_df, set_background, add_logo

#
# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

def load_data(file):
    df = _df_from_str(file.read().decode())
    df = add_timestamps_df(df)

    if 'data' not in st.session_state:
        st.session_state['data'] = df



def main():
    set_background()

    add_logo()
    st.title("WhatsApp Chat Group Analyzer")

    test_holder = st.empty()
    test_holder.header("Upload Data")

    uploading_holder = st.empty()
    uploaded_file = uploading_holder.file_uploader("Choose a TXT file", type=["txt"])

    how_to_holder = st.empty()
    how_to_holder.write("How to export WhatsApp chat - [Click Here](https://faq.whatsapp.com/1180414079177245)")

    if uploaded_file is not None:
        progress_bar = st.progress(0, text="Uploading...")
        load_data(uploaded_file)
        progress_bar.progress(100)
        uploading_holder.empty()
        test_holder.empty()
        how_to_holder.empty()
        st.write("Chat Uploaded Successfully!")
        # st.header("Chat Uploaded Successfully!")

        general_statistics = st.button("Get General Statistics")
        if general_statistics:
            switch_page("basic statistics")

        user_level_analysis = st.button("Get User Level Analysis")
        if user_level_analysis:
            switch_page("user level analysis'")

        geographics = st.button("Get Geographics Analysis")
        if geographics:
            switch_page("geographics")

        st.download_button(
            "Press to Download as CSV",
            st.session_state['data'].to_csv(index=False),
            "file.csv",
            "text/csv",
            key='download-csv'
        )


if __name__ == "__main__":
    main()
