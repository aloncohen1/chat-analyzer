import streamlit as st
import streamlit_analytics
from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.dataframe_explorer import dataframe_explorer
import re

from utils.dl_utils import get_conv_df, get_sum_text, wake_up_model
from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css
from streamlit_plotly_events import plotly_events
from utils.graphs_utils import generate_message_responses_flow, user_message_responses_heatmap, \
    generate_activity_overtime, generate_piechart, generate_users_activity_overtime
from utils.text_utils import get_users_top_worlds
from annotated_text import annotated_text, annotation


def rename_df_cols(df, language, inverse=False):
    # {col: col.capitalize() for col in df.columns}
    cols_lang_dict = {'en': {'date':'Date','timestamp':'Timestamp','username':'Username','message':'Message'},
                      'he': {'date':'תאריך','timestamp':'שעה','username':'משתמש','message': 'הודעה'}}
    if inverse:
        for lan in cols_lang_dict.keys():
            cols_lang_dict[lan] = {v: k for k, v in cols_lang_dict[lan].items()}
    df = df[cols_lang_dict[language].keys()]
    return df.rename(columns=cols_lang_dict[language])





def main():

    wake_up_model()
    st.set_page_config(layout="wide", page_title="Text Analysis", page_icon="🔀")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date, language = add_filters()

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))

        header_text = {'en': 'Text Analysis', 'he': 'ניתוח טקסט'}
        st.subheader(header_text[language])

        st.markdown(local_css("streamlit_app/streamlit/styles/metrics.css"), unsafe_allow_html=True)

        conv_df = filtered_df.copy()

        col0, col1 = st.columns((2, 5))
        with col0:
            filtered_df = dataframe_explorer(rename_df_cols(filtered_df, language), case=False)
            filtered_df = rename_df_cols(filtered_df, language, inverse=True)
        with col1:
            gran_lang_dict = {'en': ["Overall chat Activity", "Activity by user", "Activity Share"],
                              'he': ["פעילות כללית על פני זמן", "פעילות משתמשים על פני זמן", "אחוז פעילות לפי משתמש"]}
            tab_0, tab_1, tab_2 = st.tabs(gran_lang_dict[language])
            tab_0.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'date'),use_container_width=True)
            tab_1.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "date"), use_container_width=True)
            tab_2.plotly_chart(generate_piechart(filtered_df, language), use_container_width=True)
        if not filtered_df.empty:
            st.dataframe(rename_df_cols(filtered_df, language), use_container_width=True)

        st.subheader('Conversations Summarizer (Beta)')

        col1, col2, col3 = st.columns((2, 5, 5))

        conv_agg_df = get_conv_df(conv_df)

        with col1:
            date = st.selectbox('Select a Date', conv_agg_df['date'].unique())
            conv_df_to_sum = conv_agg_df[conv_agg_df['date'] == date][['preproc_text']] \
                .rename({'preproc_text': 'Conversation'}).reset_index(drop=True)
            conv_df_to_sum['Conversations'] = 'Conversation ' + (conv_df_to_sum.index+1).astype(str)

            conv = st.selectbox('Select a Conversation', conv_df_to_sum['Conversations'].to_list())
            # st.metric(f'Overall Conversations', len(conv_df_to_sum))
            st.write('')
            st.write('')
            st.write('')
            sum_bool = st.button('Summarize Conversations')
        orig_text = conv_df_to_sum[conv_df_to_sum['Conversations'] == conv]['preproc_text'].iloc[0]
        col2.subheader("Original Conversation")
        col2.write("------")
        for row in orig_text.split('\n'):
            col2.write(row)

        with col3:
            if sum_bool:
                with st.spinner('Summarizing...'):
                    st.subheader("Summarized Conversation")
                    st.write("------")
                    try:
                        preds = get_sum_text(conv_df_to_sum['preproc_text'].to_list())
                        conv_df_to_sum['sum_text'] = preds
                        sum_text = conv_df_to_sum[conv_df_to_sum['Conversations'] == conv]['sum_text'].iloc[0]
                        st.write(sum_text)
                    except Exception as e:
                        st.write("Somthing went wrong, please try again in a few seconds")


        #

        # selected_points = plotly_events(generate_activity_overtime(filtered_df, min_date, max_date,language, "Messages", 'date'))
        # st.write(selected_points)


        # col0, col1 = st.columns((15, 10))
        # with col0:
        #     with st.spinner('Wait for it...'):
        #
        #         users_top_words_df = get_users_top_worlds(filtered_df, top_words=5)
        #         users_top_words_df['show_text'] = [True] + [False] * (len(users_top_words_df) - 1)
        #         edited_df = st.data_editor(users_top_words_df, num_rows="dynamic")
        #         usernames = edited_df[edited_df["show_text"]].index.to_list()
        #
        # with col1:
        #     for username in usernames:
        #         # st.write(username)
        #         for word in users_top_words_df.drop('show_text', axis=1).loc[username]:
        #             temp_df = st.session_state['data'][(st.session_state['data']['username']==username) &
        #                                      (st.session_state['data']['message'].str.contains(f' {word}'))]\
        #                 [['username','message', "timestamp"]]
        #             temp_df['word'] = word
        #             if not temp_df.empty:
        #                 # st.write(temp_df)
        #                 for row in temp_df.itertuples():
        #                     # print(row)
        #                     # row,index = row
        #                     mes = row.message.split()
        #                     st.write(f'{row.username}, {row.timestamp}:')
        #                     annotated_text([(str(x), "") if x in word else x+' ' for x in mes])
        #                     # #
        #                     # annotated_text([(str(x), "") if bool(re.findall(fr'\s?[.,;!?]\s{re.escape(word)}\s?[.,;!?]',word))
        #                     #                 else x+' ' for x in mes])
        #
        #                     st.write('-----')




        # st.write(get_users_top_worlds(st.session_state['data']), use_container_width=True)

        # edited_df = st.experimental_data_editor(users_top_words_df)





if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    button(username="bigalon1991", width=221)
    streamlit_analytics.stop_tracking()
