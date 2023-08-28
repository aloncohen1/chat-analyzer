import pandas as pd
import streamlit as st
from utils.general_utils import refer_to_load_data_section, set_background
import plotly.express as px

st.set_page_config(layout="wide")
def generate_monthly_activity(df):
    fig = px.line(df.groupby('month', as_index=False).agg(n_message=('username', 'count')),
                  x='month', y='n_message')
    fig['data'][0]['line']['color'] = "#24d366"
    fig.update_layout(autosize=True, width=400, height=400)
    return fig

def generate_hourly_activity(df):
    fig = px.bar(df['hour'].value_counts(normalize=True).sort_index().reset_index()\
                 .rename(columns={'hour': '% of Activity',
                                  'index': 'Hour of day'}),
                 x="Hour of day", y="% of Activity", title='n_message')

    fig.update_traces(marker_color="#24d366")

    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(autosize=True, width=400, height=400)

    return fig


def generate_piechart(df,top_n=10):

    top_n = min(top_n, df["username"].nunique())

    agg_df = df["username"].value_counts(normalize=True)[0:top_n].reset_index()

    agg_df = agg_df.append(pd.DataFrame(data=[[1-agg_df["username"].sum(), 'Other']],
                                        columns=["username", "index"]))\
        .rename(columns={'username': '% of Message', 'index': 'Username'})

    fig = px.pie(agg_df, values="% of Message", names='Username', title='Rows per Username', hole=0.5,
                     color_discrete_map={"Other": 'rgb(36, 211, 102)'})  #"#24d366"

    fig.update_traces(marker=dict(line=dict(color='black', width=2)))
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_traces(showlegend=False)
    fig.update_layout(autosize=True,width=400,height=400)

    return fig #st.plotly_chart(pie_fig, use_container_width=True) # use_container_width=True



def main():

    set_background()

    if 'data' not in st.session_state:
        refer_to_load_data_section()

    else:
        st.title("WhatsApp Group Chat Analyzer")

        min_date = st.session_state['data']['date'].min()
        max_date = st.session_state['data']['date'].max()

        section = st.slider("Time Period",min_date ,max_date, (min_date,max_date))

        type(section[0])

        filtered_df = st.session_state['data'][st.session_state['data']['date'].between(section[0], section[1])]

        st.header("Data Visualization")
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Users", f"{filtered_df['username'].nunique():,}")
        col2.metric("Overall Messages", f"{filtered_df.shape[0]:,}")
        col3.metric("Active Days", f"{filtered_df['date'].nunique():,}")

        col4,col6 = st.columns((20, 20))

        col4.plotly_chart(generate_piechart(filtered_df),use_container_width=True)
        # col5.plotly_chart(generate_hourly_activity(filtered_df),use_container_width=True)
        col6.plotly_chart(generate_monthly_activity(filtered_df),use_container_width=True)

        # st.plotly_chart(generate_monthly_activity(st.session_state['data']))
        # st.plotly_chart(generate_piechart(st.session_state['data']))
        # st.plotly_chart(generate_hourly_activity(st.session_state['data']))


# Run the app
if __name__ == "__main__":
    main()
