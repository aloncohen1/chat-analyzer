import pandas as pd
import streamlit as st
from utils.general_utils import refer_to_load_data_section, set_background, add_logo
import plotly.express as px


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


st.set_page_config(layout="wide")
def generate_monthly_activity(df):
    fig = px.line(df.groupby('month', as_index=False).agg({'username': 'count'})\
                  .rename(columns={'username': '# of Messages'}), x='month', y='# of Messages')
    fig['data'][0]['line']['color'] = "#24d366"
    fig.update_layout(title_text='Chat Activity Over Time')
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")
    return fig

def generate_hourly_activity(df):
    fig = px.bar(df['hour'].value_counts(normalize=True).sort_index().reset_index()\
                 .rename(columns={'hour': '% of Activity',
                                  'index': 'Hour of day'}),
                 x="Hour of day", y="% of Activity")

    fig.update_traces(marker_color="#24d366")

    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(title_text='Activity by Hour of Day')
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig

def generate_weekly_activity(df):

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday", "Sunday"]

    fig = px.bar(df['day_name'].value_counts(normalize=True)[days_order].reset_index()\
                 .rename(columns={'day_name': '% of Activity',
                                  'index': 'Day of Week'}),
                 x="Day of Week", y="% of Activity")

    fig.update_traces(marker_color="#24d366")

    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(title_text='Activity by Day of Week')
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig

def generate_piechart(df,top_n=10):

    top_n = min(top_n, df["username"].nunique())

    agg_df = df["username"].value_counts(normalize=True)[0:top_n].reset_index()

    agg_df = agg_df.append(pd.DataFrame(data=[[1-agg_df["username"].sum(), 'Other']],
                                        columns=["username", "index"]))\
        .rename(columns={'username': '% of Message', 'index': 'Username'})

    fig = px.pie(agg_df, values="% of Message", names='Username', hole=0.5)
    # color_discrete_map={"Other": 'rgb(36, 211, 102)'}

    fig.update_traces(marker=dict(line=dict(color='black', width=2)))
    fig.update_layout(title_text='Activity Share by Username')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_traces(showlegend=False)
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")


    return fig


def main():

    set_background()
    add_logo()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:

        min_date = st.session_state['data']['date'].min()
        max_date = st.session_state['data']['date'].max()

        st.sidebar.write('')
        time_filter = st.sidebar.slider("Time Period", min_date, max_date, (min_date, max_date))

        st.sidebar.write('')

        users_filter = st.sidebar.multiselect("Users", ["All"] + list(st.session_state['data']['username'].unique()),
                                              default='All')
        if "All" in users_filter:
            filtered_df = st.session_state['data']
        else:
            filtered_df = st.session_state['data'][st.session_state['data']['username'].isin(users_filter)]

        filtered_df = filtered_df[filtered_df['date'].between(time_filter[0], time_filter[1])]

        local_css("streamlit_app/streamlit/styles/metrics.css")

        col1, col2, col3 = st.columns([5,4,1.5],gap='large')
        col1.metric("Overall Users", f"{filtered_df['username'].nunique():,}",)
        col2.metric("Overall Messages", f"{filtered_df.shape[0]:,}")
        col3.metric("Active Days", f"{filtered_df['date'].nunique():,}")

        col4, col5 = st.columns((6, 10))

        col4.plotly_chart(generate_piechart(filtered_df), use_container_width=True)
        col5.plotly_chart(generate_monthly_activity(filtered_df), use_container_width=True)

        col6, col7 = st.columns((6, 10))

        col6.plotly_chart(generate_weekly_activity(filtered_df), use_container_width=True)
        col7.plotly_chart(generate_hourly_activity(filtered_df), use_container_width=True)


# Run the app
if __name__ == "__main__":
    main()
