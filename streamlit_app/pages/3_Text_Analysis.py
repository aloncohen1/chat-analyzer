import streamlit as st
import streamlit_analytics
from streamlit_extras.buy_me_a_coffee import button


from utils.dl_utils import get_conv_df, get_sum_text, wake_up_model
from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css

from utils.graphs_utils import generate_activity_overtime, generate_piechart, generate_users_activity_overtime


COLS_LANG_DICT = {'en': {'date': 'Date', 'week': 'Week', 'month': 'Month', 'timestamp': 'Timestamp',
                         'username': 'Username', 'message': 'Message'},
                  'he': {'date': 'תאריך', 'week': 'שבוע', 'month': 'חודש', 'timestamp': 'שעה',
                         'username': 'משתמש', 'message': 'הודעה'}}


def rename_df_cols(df, language, inverse=False):

    if inverse:
        for lan in COLS_LANG_DICT.keys():
            COLS_LANG_DICT[lan] = {v: k for k, v in COLS_LANG_DICT[lan].items()}
    df = df[COLS_LANG_DICT[language].keys()]
    return df.rename(columns=COLS_LANG_DICT[language])


# def update(change):
#     if change == 'slider':
#         print(st.session_state.slider)
#     else:
#         print(st.session_state.date_input)
#         if len(st.session_state.date_input) > 1:
#             min_date, max_date = st.session_state.date_input
#         else:
#             min_date, max_date = st.session_state.date_input[0], st.session_state.date_input[0] + timedelta(days=1)
#         st.session_state.slider = min_date, max_date

    # min_date, max_date = st.date_input("", (min_date, max_date), global_min_date, global_max_date, key='date_input',
    #                                    on_change=update, args=('date_input',))


def main():

    wake_up_model()
    st.set_page_config(layout="wide", page_title="Text Analysis", page_icon="📃")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, _, _, language = add_filters(add_side_filters=False)
        min_date, max_date = filtered_df['date'].min(), filtered_df['date'].max()

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))

        st.markdown(local_css("streamlit_app/streamlit/styles/metrics.css"), unsafe_allow_html=True)

        conv_df = filtered_df.copy()

        global_title_lang_dict = {'en': 'Text Analysis', 'he': "ניתוח טקסט"}
        st.subheader(global_title_lang_dict[language])

        global_col, _ = st.columns((1000, 0.10))
        with global_col:
            explorer_title_lang_dict = {'en': 'Explode Your Chat', 'he': "חקור/י את הצ'אט שלך"}
            st.subheader(explorer_title_lang_dict[language])
            st.divider()
            filters_col0, filters_col1, filters_col2 = st.columns((1, 1, 2))
            with filters_col0:
                date_lang_dict = {'en': 'Period', 'he': "תקופה"}
                min_date, max_date = st.slider(date_lang_dict[language], min_date, max_date, (min_date, max_date))
                filtered_df = filtered_df[filtered_df['date'].between(min_date, max_date)]

            with filters_col1:
                users_lang_dict = {'en': 'Users', 'he': "משתמשים"}
                all_dict = {'en': 'All', 'he': "כולם"}
                users_filter = st.multiselect(users_lang_dict[language],
                                              [all_dict[language]] + list(st.session_state['data']['username'].unique()),
                                              default=all_dict[language])
                if all_dict[language] in users_filter or not users_filter:
                    pass
                else:
                    filtered_df = filtered_df[filtered_df['username'].isin(users_filter)]

            with filters_col2:
                text_input_lang = {'en': "Search by Text", 'he': "טקסט"}
                free_text = st.text_input(text_input_lang[language])
                if free_text:
                    filtered_df = filtered_df[filtered_df['message'].str.lower().str.contains(free_text.lower())]
            st.divider()
            col0, col1 = st.columns((5, 5))
            with col0:

                filtered_df = rename_df_cols(filtered_df, language)

                temp_df = filtered_df[[COLS_LANG_DICT[language]['username'],
                                       COLS_LANG_DICT[language]['timestamp'],
                                       COLS_LANG_DICT[language]['message']]]

                temp_df[COLS_LANG_DICT[language]['message']] = temp_df[COLS_LANG_DICT[language]['username']] \
                                                               + ' ('+ temp_df[COLS_LANG_DICT[language]['timestamp']]\
                                                                   .astype(str)+ '): ' + \
                                                               temp_df[COLS_LANG_DICT[language]['message']]

                st.dataframe(temp_df[COLS_LANG_DICT[language]['message']], use_container_width=True, height=560, hide_index=True)
                filtered_df = rename_df_cols(filtered_df, language, inverse=True)
            with col1:
                section_lang_dict = {'en': ["Overall chat Activity", "Activity by user", "Activity Share"],
                                  'he': ["פעילות כללית על פני זמן", "פעילות משתמשים על פני זמן", "אחוז פעילות לפי משתמש"]}

                tab_0, tab_1, tab_2 = st.tabs(section_lang_dict[language])
                with tab_0:
                    gran_lang_dict = {'en': ["Monthly", "Weekly", "Daily"], 'he': ["חודשי", "שבועי", "יומי"]}
                    sub0_0, sub0_1, sub0_2 = st.tabs(gran_lang_dict[language])
                    sub0_0.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'month'),use_container_width=True)
                    sub0_1.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'week'),use_container_width=True)
                    sub0_2.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'date'),use_container_width=True)
                with tab_1:
                    sub1_0, sub1_1, sub1_2 = st.tabs(gran_lang_dict[language])
                    sub1_0.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "month"),
                                        use_container_width=True)
                    sub1_1.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "week"),
                                        use_container_width=True)
                    sub1_2.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "date"),
                                        use_container_width=True)

                tab_2.plotly_chart(generate_piechart(filtered_df, language), use_container_width=True)

        global_col1, _ = st.columns((1000, 0.1))
        with global_col1:
            summrizer_title_lang_dict = {'en': 'Conversations Summarizer (Beta)', 'he': '(Beta) מסכם שיחות'}
            st.subheader(summrizer_title_lang_dict[language])
            st.divider()

            col1, col2, col3 = st.columns((2, 5, 5))

            conv_agg_df = get_conv_df(conv_df)

            with col1:
                date_selector_lng_dict = {'en': 'Select a Date', 'he': 'בחר תאריך'}
                month_selector_lng_dict = {'en': 'Select a Month', 'he': 'בחר חודש'}
                conf_filed_lan_dict = {'en': 'Conversation', 'he': "שיחה"}

                month = st.selectbox(month_selector_lng_dict[language], conv_agg_df['month'].unique())

                date = st.selectbox(date_selector_lng_dict[language],
                                    conv_agg_df[conv_agg_df['month'] == month]['date'].unique())
                conv_df_to_sum = conv_agg_df[conv_agg_df['date'] == date][['preproc_text']] \
                    .rename({'preproc_text': 'Conversation'}).reset_index(drop=True)
                conv_df_to_sum['Conversations'] = f'{conf_filed_lan_dict[language]} ' + (conv_df_to_sum.index+1).astype(str)

                conv_selector_lang_dict = {'en': 'Select a Conversation', 'he': "בחר שיחה"}
                all_lang_dict = {'en': 'All', 'he': "כל השיחות"}
                conv = st.selectbox(conv_selector_lang_dict[language],[all_lang_dict[language]] + conv_df_to_sum['Conversations'].to_list())
                # st.metric(f'Overall Conversations', len(conv_df_to_sum))
                st.write('')
                st.write('')
                st.write('')
                button_lang_dict = {'en': 'Summarize Conversations', 'he': "סכם שיחות"}
                sum_bool = st.button(button_lang_dict[language])
            if conv not in all_lang_dict.values():
                orig_text = conv_df_to_sum[conv_df_to_sum['Conversations'] == conv]['preproc_text'].iloc[0]
                orig_text = [orig_text]
                conv_ids = [conv]
            else:
                orig_text = conv_df_to_sum["preproc_text"].to_list()
                conv_ids = conv_df_to_sum["Conversations"].to_list()
            orig_text_lang_dict = {'en': "Original Conversation", 'he': "שיחה מקורית"}
            col2.subheader(orig_text_lang_dict[language])
            col2.write("------")
            for conv_id, orig_text_i in zip(conv_ids, orig_text):
                # col2.write(f'Conversation {conv_index}')
                col2.markdown(f'<div style="text-align: right;"><b><u>{conv_id}</b></u></div>', unsafe_allow_html=True)
                for index, row in enumerate(orig_text_i.split('\n')):
                    col2.write(row)
                col2.write("------")
                # direct = 'left' if index % 2 == 0 else 'right'
                # col2.markdown(f'<div style="text-align: {direct};">{row}</div>', unsafe_allow_html=True)

            with col3:
                sum_text_lang_dict = {'en': "Summarized Conversation", 'he': "שיחה מסוכמת"}
                st.subheader(sum_text_lang_dict[language])
                st.write("------")
                if sum_bool:
                    with st.spinner('Summarizing...'):
                        try:
                            preds = get_sum_text(conv_df_to_sum['preproc_text'].to_list())
                            conv_df_to_sum['sum_text'] = preds

                            if conv not in all_lang_dict.values():
                                sum_text = conv_df_to_sum[conv_df_to_sum['Conversations'] == conv]['sum_text'].iloc[0]
                                sum_text = [sum_text]
                            else:
                                sum_text = conv_df_to_sum["sum_text"].to_list()

                            for conv_id, sum_text_i in zip(conv_ids, sum_text):
                                st.markdown(f'<div style="text-align: right;"><b><u>{conv_id}</b></u></div>', unsafe_allow_html=True)
                                st.write(sum_text_i)
                                st.write("------")
                        except Exception as e:
                            st.write("Somthing went wrong, please try again in a few seconds")
                            st.write(e)

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
