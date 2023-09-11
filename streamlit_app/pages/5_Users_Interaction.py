import streamlit as st
import streamlit_analytics


from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css
from utils.graphs_utils import generate_message_responses_flow, user_message_responses_heatmap



def main():
    st.set_page_config(layout="wide", page_title="Users Interaction", page_icon="🔀")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date = add_filters()

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))
        st.subheader('Users Interaction')


        st.markdown(local_css("streamlit_app/streamlit/styles/metrics.css"), unsafe_allow_html=True)


        st.plotly_chart(generate_message_responses_flow(filtered_df,5), use_container_width=True)
        st.plotly_chart(user_message_responses_heatmap(filtered_df,10), use_container_width=True)



        # st.write(get_users_top_worlds(st.session_state['data']), use_container_width=True)

        # edited_df = st.experimental_data_editor(users_top_words_df)





if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    streamlit_analytics.stop_tracking()
