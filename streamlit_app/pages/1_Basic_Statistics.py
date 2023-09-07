
import streamlit as st
from utils.general_utils import refer_to_load_data_section, set_background, add_logo, add_filters, local_css
from utils.graphs_utils import generate_piechart, generate_activity_overtime, generate_weekly_activity, \
    generate_hourly_activity, generate_activity_matrix


def main():

    st.set_page_config(layout="wide", page_title="Geographics", page_icon="📊")
    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:

        filtered_df, min_date, max_date = add_filters()

        st.markdown(local_css("streamlit_app/streamlit/styles/metrics.css"), unsafe_allow_html=True)

        if st.session_state.get('file_name'):
            st.header(st.session_state.get('file_name'))
        st.subheader('Basic Statistics')

        col1, col2, col3 = st.columns([5, 4, 1.5], gap='large')
        col1.metric("Overall Users", f"{filtered_df['username'].nunique():,}",)
        col2.metric("Overall Messages", f"{filtered_df.shape[0]:,}")
        col3.metric("Active Days", f"{filtered_df['date'].nunique():,}")

        col4, col5 = st.columns((6, 10))

        col4.plotly_chart(generate_piechart(filtered_df), use_container_width=True)
        with col5:
            unit = st.selectbox("Messages / Users", ("Messages", "Users"))
            tab_0, tab_1, tab_2 = st.tabs(["Monthly", "Weekly", "Daily"])
            tab_0.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, unit, "month"), use_container_width=True)
            tab_1.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, unit, 'week'), use_container_width=True)
            tab_2.plotly_chart(generate_activity_overtime(filtered_df, min_date, max_date, unit, 'date'), use_container_width=True)

        col6, col7 = st.columns((6, 10))

        col6.plotly_chart(generate_weekly_activity(filtered_df), use_container_width=True)
        col7.plotly_chart(generate_hourly_activity(filtered_df), use_container_width=True)

        st.plotly_chart(generate_activity_matrix(filtered_df), use_container_width=True)

        st.write(filtered_df[0:100])


# Run the app
if __name__ == "__main__":
    main()
