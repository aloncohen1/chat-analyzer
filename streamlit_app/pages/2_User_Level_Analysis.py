import streamlit as st
import numpy as np
from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css
from utils.graphs_utils import generate_message_responses_flow
from PIL import Image


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
        return users_per_row, users_per_row
    else:
        return np.floor(top_n_users / 2.0), np.ceil(top_n_users / 2.0)



def main():

    st.set_page_config(layout="wide")
    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        image = Image.open("streamlit_app/streamlit/styles/logos/user_logo.jpg")

        filtered_df, min_date, max_date = add_filters()
        # col0, col1 = st.columns((10, 10))
        # with col0:
        #     with st.container():
        #         st.image(image, caption='Avi', width=100)
        #         st.metric('n messeges', 100)
        #         st.metric('n words', 20)
        #         st.metric('n days', 10)
        #     st.plotly_chart(generate_message_responses_flow(filtered_df), use_container_width=True)
        #     # You can create a similar template for each section as the main app


        top_n_users = min(filtered_df['username'].nunique(), 9)
        st.write(f'min users: {top_n_users}')

        row_a_n_users, row_b_n_users = calc_n_user_per_row(top_n_users)
        st.write(f'row a: {row_a_n_users}')
        st.write(f'row b: {row_b_n_users}')

        row_a = st.columns(np.array(int(row_a_n_users) * [10]))
        row_b = st.columns(np.array(int(row_b_n_users) * [10]))

        for col in row_a:
            with col:
                center_photo()
                st.image(image, caption='Avi', width=100)
                st.metric('n messeges', 100)
                st.metric('n words', 20)
                st.metric('n days', 10)

        for col in row_b:
            with col:
                center_photo()
                st.image(image, caption='Avi', width=100)
                st.metric('n messeges', 100)
                st.metric('n words', 20)
                st.metric('n days', 10)


        add_metric_black_b()


        # st.markdown(css_body_container, unsafe_allow_html=True)





        # conversation = st.sidebar.multiselect("Conversation", list(filtered_df['conversation_id'].unique()))
        #
        # st.write(filtered_df[filtered_df['conversation_id'].isin(conversation)])


# Run the app
if __name__ == "__main__":
    main()
