import streamlit as st
import streamlit_analytics
import pandas as pd
import re
from streamlit_extras.buy_me_a_coffee import button
from annotated_text import annotated_text

from app_utils.dl_utils import get_conv_df, get_sum_text, wake_up_models, run_trans, apply_hg_model, API_URL_SENTIMENT
from app_utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css, \
    linkedin_link, form_link, buy_me_a_coffee_link

from app_utils.graphs_utils import generate_activity_overtime, generate_piechart, generate_users_activity_overtime, \
    generate_sentiment_piehart, generate_sentiment_bars
from app_utils.text_utils import detect_lang, human_format, stream_data

import nltk
if not st.session_state.get('punkt_downloaded'):
    nltk.download('punkt')
    st.session_state['punkt_downloaded'] = True
from nltk import tokenize

COLS_LANG_DICT = {'en': {'date': 'Date', 'week': 'Week', 'month': 'Month', 'timestamp': 'Timestamp',
                         'username': 'Username', 'message': 'Message'},
                  'he': {'date': 'תאריך', 'week': 'שבוע', 'month': 'חודש', 'timestamp': 'שעה',
                         'username': 'משתמש', 'message': 'הודעה'}}

def get_summarizer_df(filtered_df, language):
    sum_text_col1, _ = st.columns((1000, 0.1))
    with sum_text_col1:
        summrizer_title_lang_dict = {'en': 'Conversations Summarizer (Beta)', 'he': '(Beta) מסכם שיחות'}
        st.subheader(summrizer_title_lang_dict[language])
        st.divider()

        filter_col0, filter_col1, filter_col2, button_col = st.columns((1, 1, 1, 1))

        conv_df = filtered_df.copy()

        conv_agg_df = get_conv_df(conv_df)

        date_selector_lng_dict = {'en': 'Select a Date', 'he': 'בחר תאריך'}
        month_selector_lng_dict = {'en': 'Select a Month', 'he': 'בחר חודש'}
        conf_filed_lan_dict = {'en': 'Conversation', 'he': "שיחה"}

        with filter_col0:

            month = st.selectbox(month_selector_lng_dict[language], conv_agg_df['month'].unique())

        with filter_col1:

            date = st.selectbox(date_selector_lng_dict[language],
                                conv_agg_df[conv_agg_df['month'] == month]['date'].unique())

        conv_df_to_sum = conv_agg_df[conv_agg_df['date'] == date][['preproc_text']] \
            .rename({'preproc_text': 'Conversation'}).reset_index(drop=True)
        conv_df_to_sum['Conversations'] = f'{conf_filed_lan_dict[language]} ' + (conv_df_to_sum.index + 1).astype(
            str)


        with filter_col2:
            conv_selector_lang_dict = {'en': 'Select a Conversation', 'he': "בחר שיחה"}
            all_lang_dict = {'en': 'All', 'he': "כל השיחות"}
            conv = st.selectbox(conv_selector_lang_dict[language],
                                [all_lang_dict[language]] + conv_df_to_sum['Conversations'].to_list())
            # st.metric(f'Overall Conversations', len(conv_df_to_sum))

        with button_col:
            button_lang_dict = {'en': 'Summarize Conversations', 'he': "סכם שיחות"}
            st.write('')
            st.write('')
            sum_bool = st.button(button_lang_dict[language],key='sum')

        st.divider()
        col2, col3 = st.columns((5, 5))

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
                            st.markdown(f'<div style="text-align: right;"><b><u>{conv_id}</b></u></div>',
                                        unsafe_allow_html=True)
                            st.write_stream(stream_data(sum_text_i))
                            st.write("------")
                    except Exception as e:
                        st.write("Somthing went wrong, please try again in a few seconds")
                        st.write(e)

def rename_df_cols(df, language, inverse=False):

    if inverse:
        for lan in COLS_LANG_DICT.keys():
            COLS_LANG_DICT[lan] = {v: k for k, v in COLS_LANG_DICT[lan].items()}
    df = df[COLS_LANG_DICT[language].keys()]
    return df.rename(columns=COLS_LANG_DICT[language])


def get_trends_explorer_widgets(filtered_df, min_date, max_date, language):

    global_col, _ = st.columns((1000, 0.10))
    with global_col:
        explorer_title_lang_dict = {'en': 'Trends Analysis', 'he': "חקור/י את הצ'אט שלך"}
        st.subheader(explorer_title_lang_dict[language])

        st.divider()

        text_input_lang = {'en': "Filter by text", 'he': "סנן על פי טקסט"}
        free_text = st.text_input(text_input_lang[language], key='trends_text')
        if free_text:
            filtered_df = filtered_df[filtered_df['message'].str.lower().str.contains(free_text.lower())]

        col0, col1 = st.columns((5, 5))

        with col0:
            filtered_df = rename_df_cols(filtered_df, language)

            temp_df = filtered_df[[COLS_LANG_DICT[language]['username'],
                                   COLS_LANG_DICT[language]['timestamp'],
                                   COLS_LANG_DICT[language]['message']]]

            temp_df[COLS_LANG_DICT[language]['message']] = temp_df[COLS_LANG_DICT[language]['username']] \
                                                           + ' (' + temp_df[COLS_LANG_DICT[language]['timestamp']] \
                                                               .astype(str) + '): ' + \
                                                           temp_df[COLS_LANG_DICT[language]['message']]

            st.dataframe(temp_df[COLS_LANG_DICT[language]['message']], use_container_width=True, height=560,
                         hide_index=True)

            filtered_df = rename_df_cols(filtered_df, language, inverse=True)
        with col1:
            section_lang_dict = {'en': ["Overall chat Activity", "Activity by user", "Activity Share"],
                              'he': ["פעילות כללית על פני זמן", "פעילות משתמשים על פני זמן", "אחוז פעילות לפי משתמש"]}

            tab_0, tab_1, tab_2 = st.tabs(section_lang_dict[language])
            with tab_0:
                gran_lang_dict = {'en': ["Monthly", "Weekly", "Daily"], 'he': ["חודשי", "שבועי", "יומי"]}
                sub0_0, sub0_1, sub0_2 = st.tabs(gran_lang_dict[language])
                sub0_0.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'month'), use_container_width=True)
                sub0_1.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'week'), use_container_width=True)
                sub0_2.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, language, "Messages", 'date'), use_container_width=True)
            with tab_1:
                sub1_0, sub1_1, sub1_2 = st.tabs(gran_lang_dict[language])
                sub1_0.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "month"),
                                    use_container_width=True)
                sub1_1.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "week"),
                                    use_container_width=True)
                sub1_2.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "date"),
                                    use_container_width=True)

            tab_2.plotly_chart(generate_piechart(filtered_df, language), use_container_width=True)

    return filtered_df

@st.cache_data(show_spinner=False)
def calc_sentimnets(filtered_df,term, chat_lang, max_words, max_messages, sample_size):
    pattern = f'[^a-zA-Zא-ת]{term.lower()}[^a-zA-Zא-ת]'
    pred_df = filtered_df[(filtered_df['message'].str.lower().str.contains(term.lower())) &
                          (filtered_df['message'].str.lower().str.contains(pattern)) &
                          (filtered_df['text_length'] <= max_words)]
    if len(pred_df) >= max_messages:
        pred_df = pred_df.groupby(['username', 'month'], group_keys=False) \
            .apply(lambda x: x.sample(frac=sample_size, replace=True))
    if not pred_df.empty:

        sent_df = pred_df['message'].map(tokenize.sent_tokenize).explode()
        sent_df = sent_df[sent_df.str.lower().str.contains(term.lower())].reset_index().rename(
            columns={'message': 'sent'})
        sent_df['sent_length'] = sent_df['sent'].str.split().apply(len)
        sent_df = sent_df.sort_values(['index', 'sent_length']).drop_duplicates(subset=['index'], keep='first')

        sent_df['text_to_trans'] = ('[CLS] ' + sent_df['sent'] + f' [SEP] {term} [SEP]').to_list()
        sent_df = sent_df.head(min(max_messages, len(sent_df)))

        if chat_lang != 'en':
            trans_text = run_trans(sent_df['text_to_trans'].to_list())
            sent_df['text_to_pred'] = [i.get('translation') for i in trans_text]
        else:
            sent_df['text_to_pred'] = sent_df['text_to_trans']

        pred_df = pred_df.merge(sent_df, left_index=True, right_on='index')

        sentiments_pred = apply_hg_model(sent_df['text_to_pred'].to_list(), API_URL_SENTIMENT)

        pred_df = pred_df.reset_index(drop=True).join(
            pd.concat([pd.DataFrame(i).sort_values('score', ascending=False).head(1) for i in sentiments_pred],
                      ignore_index=True))
        return pred_df

    else:
        st.title(f'"{term}" not seem to appear in Chat')


@st.spinner('Caculating Sentiment....')
def get_sentiment_widget(filtered_df, language, max_words=30, max_messages=300, sample_size=0.2):

    if not st.session_state.get('lang'):
        detect_lang(filtered_df)
    chat_lang = st.session_state['lang']

    global_col,_ = st.columns((1000,0.1))

    with global_col:

        st.subheader('Sentiment Analysis')
        st.divider()
        text_input_lang = {'en': "Select Term", 'he': "בחר מילה"}
        term = st.text_input(text_input_lang[language], key='sentiment')

        if not term:
            pass
        else:
            pred_df = calc_sentimnets(filtered_df, term, chat_lang, max_words, max_messages, sample_size)

            col0, col1 = st.columns((1,2))
            # colors_text_dict = {'Negative':'#FEEDEC','Neutral':'#FFF8E0','Positive':'#E4F8ED'}
            colors_dict = {'Negative':'#ff5a5a','Neutral':'#ffb119','Positive':'#27b966'}
            col0.plotly_chart(generate_sentiment_piehart(pred_df,colors_dict),use_container_width=True)
            col1.plotly_chart(generate_sentiment_bars(pred_df,colors_dict),use_container_width=True)

            sent_example_col,_ = st.columns((100,0.1))

            with sent_example_col:
                for _, row in pred_df[['message', 'label','username','timestamp','score']].iterrows():
                    if row.label in colors_dict.keys():
                        st.write(f'{row.username} ({row.timestamp}):')
                        annot = ((i+' ', row.label,colors_dict.get(row.label),'black')\
                                     if term.lower() in i.lower() else i+' ' for i in row.message.split())
                        annotated_text(*annot)
                        st.write('*Confidence Score: %s*' % human_format(row.score))
                        st.divider()


def main():

    wake_up_models()
    st.set_page_config(layout="wide", page_title="Text Analysis", page_icon="📃")
    add_logo()
    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        filtered_df, min_date, max_date, language = add_filters()

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))

        st.markdown(local_css("add_ons/styles/metrics.css"), unsafe_allow_html=True)

        global_title_lang_dict = {'en': 'Text Analysis (NLP)', 'he': "ניתוח טקסט (NLP)"}
        st.subheader(global_title_lang_dict[language])

        trend_tab, sentiment_tab, sum_tab = st.tabs(['**Trends Analysis**', '**Sentiment Analysis**',
                                                     '**Conversations Summarizer (Beta)**'])

        with trend_tab:
            get_trends_explorer_widgets(filtered_df, min_date, max_date, language)

        with sentiment_tab:
            get_sentiment_widget(filtered_df,language)

        with sum_tab:
            get_summarizer_df(filtered_df, language)






if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    # button(username="bigalon1991", width=221)
    linkedin_link()
    form_link()
    buy_me_a_coffee_link()
    streamlit_analytics.stop_tracking(unsafe_password=st.secrets["tracking_pass"])
