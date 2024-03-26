
import streamlit as st
import streamlit_analytics
from streamlit_plotly_events import plotly_events
from streamlit_extras.buy_me_a_coffee import button

from app_utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css, \
    linkedin_link, form_link, buy_me_a_coffee_link
from app_utils.graphs_utils import generate_piechart, generate_activity_overtime, generate_day_of_week_activity, \
    generate_hourly_activity, generate_activity_matrix, generate_users_activity_overtime


def main():

    st.set_page_config(layout="wide", page_title="Basic Statistics", page_icon="📊")
    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:

        filtered_df, min_date, max_date, language = add_filters()

        st.markdown(local_css("add_ons/styles/metrics.css"), unsafe_allow_html=True)

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))
        header_text = {'en': 'Basic Statistics', 'he': 'ניתוח סטטיסטי'}
        st.subheader(header_text[language])

        col1, col2, col3 = st.columns([5, 4, 1.5], gap='large')

        user_metric_text = {'en': 'Overall Users', 'he': 'סה"כ חברים בקבוצה'}
        col1.metric(user_metric_text[language], f"{filtered_df['username'].nunique():,}")

        messages_metric_text = {'en': 'Overall Messages', 'he': 'סה"כ הודעות בקבוצה'}
        col2.metric(messages_metric_text[language], f"{filtered_df.shape[0]:,}")

        days_metric_text = {'en': 'Active Days', 'he': 'סה"כ ימים'}
        col3.metric(days_metric_text[language], f"{filtered_df['date'].nunique():,}")

        col4, col5 = st.columns((6, 10))

        col4.plotly_chart(generate_piechart(filtered_df, language), use_container_width=True)
        with col5:
            unit_lang_dict = {'en': ("Messages", "Users"), 'he': ("הודעות", "משתמשים")}
            unit_dict = {"Messages": "Messages", "Users": "Users","משתמשים": "Users","הודעות": 'Messages'}
            unit_lan_title = {'en': "Messages / Users", "he": "משתמשים / הודעות"}
            unit = st.selectbox(unit_lan_title[language], unit_lang_dict[language])
            unit = unit_dict[unit]

            gran_lang_dict = {'en': ["Monthly", "Weekly", "Daily"], 'he': ["חודשי", "שבועי", "יומי"]}
            tab_0, tab_1, tab_2 = st.tabs(gran_lang_dict[language])

            tab_0.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date,language, unit, "month"), use_container_width=True)
            tab_1.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date,language, unit, 'week'), use_container_width=True)
            tab_2.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date,language, unit, 'date'), use_container_width=True)
            # with tab_2:
            #     selected_points = plotly_events(
            #         generate_activity_overtime(filtered_df, min_date, max_date, "Messages", 'date'))
            #     st.write(selected_points)

        col_users, _ = st.columns((100, 1))
        with col_users:
            tab_4, tab_5, tab_6 = st.tabs(gran_lang_dict[language])
            tab_4.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "month"), use_container_width=True)
            tab_5.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "week"), use_container_width=True)
            tab_6.plotly_chart(generate_users_activity_overtime(filtered_df, min_date, max_date, language, "date"), use_container_width=True)

        col6, col7 = st.columns((6, 10))

        col6.plotly_chart(generate_day_of_week_activity(filtered_df, language), use_container_width=True)
        col7.plotly_chart(generate_hourly_activity(filtered_df, language), use_container_width=True)

        st.plotly_chart(generate_activity_matrix(filtered_df, language), use_container_width=True)



# Run the app
if __name__ == "__main__":
    streamlit_analytics.start_tracking()
    main()
    # button(username="bigalon1991", width=221)
    linkedin_link()
    form_link()
    buy_me_a_coffee_link()
    streamlit_analytics.stop_tracking(unsafe_password=st.secrets["tracking_pass"])
