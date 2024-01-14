from time import sleep
import pandas as pd
from PIL import Image
import streamlit_analytics
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.buy_me_a_coffee import button

import streamlit as st

from app_utils.parsers import _df_from_str

from app_utils.general_utils import add_metadata_to_df, set_background, add_logo, generate_synthetic_locations, \
    app_language, linkedin_link, form_link, buy_me_a_coffee_link
from app_utils.parsers import parse_telegram_html
import streamlit.components.v1 as components

# PROD_IMAGE = Image.open("add_ons/styles/logos/prod_image.png")

WHATSAPP_IMAGE_PATH = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/240px-WhatsApp.svg.png'
TELEGRAM_IMAGE_PATH = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Telegram_2019_Logo.svg/242px-Telegram_2019_Logo.svg.png'

CHAT_EXAMPLE_PATH = 'example_chat.txt'

with open('add_ons/styles/prod_sliding_photos.html') as f:
    prod_sliding_photos = f.read()

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
    progress_bar = st.progress(0, text="Processing...")
    df_list = []
    for index, file in enumerate(files):
        if file.name.endswith('.txt'):
            df_list.append(_df_from_str(file.read().decode()))
            st.session_state['file_name'] = file.name.replace('.txt', '')\
                .replace('WhatsApp Chat with', '').replace('_','')

        elif file.name.endswith('.html'):
            try:
                group_name, group_df = parse_telegram_html(file.read().decode())
                st.session_state['file_name'] = group_name
                df_list.append(group_df)
            except:
                print(file.name)
        progress_bar.progress(((index + 1) / len(files)), text="Processing...")
    final_df = add_metadata_to_df(pd.concat(df_list, ignore_index=True)).sort_values('timestamp')
    st.session_state['data'] = final_df
    st.session_state['lang'] = None

    progress_bar.progress(100)



def main():
    # st.set_page_config(layout="wide", page_title="Hello", page_icon="👋")
    google_site_verification_code = st.secrets['google_site_verification_code']
    meta_tag = f'<meta name="google-site-verification" content="{google_site_verification_code}" />'
    st.markdown(meta_tag, unsafe_allow_html=True)

    set_background()

    add_logo()
    language = app_language()
    title = {'en': "Chat Analyzer", 'he': "!מנתח הצ'אט"}
    st.title(title[language])

    home_holder = st.empty()
    home_holder_text = {"en": "Supports Whatsapp (.txt) / Telegram (.html)","he":"Whatsapp (.txt) / Telegram (.html) - תומך ב"}

    w_photo = f'<img src="{WHATSAPP_IMAGE_PATH}" width="30" height="30">'
    t_photo = f'<img src="{TELEGRAM_IMAGE_PATH}" width="30" height="30">'

    home_holder.markdown(f'{w_photo} {t_photo} </a><span style="font-size: 20px;">{home_holder_text[language]}</span>', unsafe_allow_html=True)

    uploading_holder = st.empty()
    upload_text = {"en": "Choose a TXT / HTML file/s", "he": "TXT / HTML בחר קובץ אחד או יותר מסוג"}
    uploaded_file = uploading_holder.file_uploader(upload_text[language], type=["txt", "html"], accept_multiple_files=True)

    info_lang_dict = {'en': 'Your data is protected! nothing being saved / sent elsewhere',
                      'he': 'הדאטא שלך מוגן, הוא איננו נשמר / נשלח החוצה'}

    info_place = uploading_holder = st.empty()
    with info_place:
        st.info(info_lang_dict[language], icon="ℹ️")

    test_file_holder = st.empty()
    example_text = {"en": "Load Chat Example File", "he": "טען צ'אט לדוגמא"}
    load_test = test_file_holder.button(example_text[language], type="primary")

    prod_photo_holder = st.empty()
    with prod_photo_holder:
        st.markdown('<img src="https://github.com/aloncohen1/chat-analyzer/assets/42881311/ca7d0912-792b-4519-bd6f-b2732b84a21b" alt="drawing" style="width:1000px;"/>',
                    unsafe_allow_html=True)
        # components.html(prod_sliding_photos, height=800, width=1200)

    how_to_text_holder = st.empty()
    how_to_pic_holder = st.empty()

    with how_to_text_holder:
        whatsapp_text = {"en": "How to export WhatsApp chat ", "he": "איך לייצא את קובץ הצ'אט מווטסאפ "}
        telegram_text = {"en": "How to export Telegram chat ", "he": "איך לייצא את קובץ הצ'אט מהטלגרם "}
        clickhere_lang_dict = {"en": "Click Here", "he": "לחץ כאן"}

        image_width = 30  # Adjust this value as needed
        image_height = 30  # Adjust this value as needed
        whatsapp_html = f'''<a href="https://faq.whatsapp.com/1180414079177245/)">
        <img src="{WHATSAPP_IMAGE_PATH}" width="{image_width}" height="{image_height}"></a><span style="font-size: 20px;">{whatsapp_text[language]}</span> - 
        <a href="https://faq.whatsapp.com/1180414079177245/">{clickhere_lang_dict[language]}</a>'''

        telegram_html = f'''<a href="https://telegram.org/blog/export-and-more">
                <img src="{TELEGRAM_IMAGE_PATH}" width="{image_width}" height="{image_height}"></a><span style="font-size: 20px;">{telegram_text[language]}</span> - 
                <a href="https://telegram.org/blog/export-and-more">{clickhere_lang_dict[language]}</a>'''

        final_html = f'{whatsapp_html}<br>{telegram_html}'

        st.markdown(final_html, unsafe_allow_html=True)


    if uploaded_file:
        info_place.empty()
        prod_photo_holder.empty()
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
        info_place.empty()
        prod_photo_holder.empty()
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
    # button(username="bigalon1991", width=221,floating=False)
    linkedin_link()
    form_link()
    buy_me_a_coffee_link()

    # button(username="bigalon1991", width=221, floating=False)


    streamlit_analytics.stop_tracking(unsafe_password=st.secrets["tracking_pass"])
