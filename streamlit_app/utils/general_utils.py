import pandas as pd
from whatstk import WhatsAppChat
import streamlit as st
from whatstk.graph import FigureBuilder
from streamlit_extras.switch_page_button import switch_page
import plotly.express as px
import json
import plotly

import numpy as np

URL_PATTERN = r"(https:\/\/maps\.google\.com\/\?q=-?\d+\.\d+,-?\d+\.\d+)"

def refer_to_load_data_section():
    st.title("Please Upload Data to Analyze")
    upload_data = st.button("Take me to uploading data page!")
    if upload_data:
        switch_page("hello")

def set_background():
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("https://w0.peakpx.com/wallpaper/580/650/HD-wallpaper-whatsapp-bg-dark-background.jpg");
    background-size: contain;
    }
    </style>
    '''
    return st.markdown(page_bg_img, unsafe_allow_html=True)

def add_timestamps_df(df):

    df['timestamp'] = pd.to_datetime(df['date'])
    df['year'] = df['timestamp'].dt.year
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.floor('h').dt.strftime("%H:%M")
    df['month'] = df.timestamp.dt.to_period('M').dt.to_timestamp()
    df['epoch_dt'] = (df['month'].astype(np.int64) // 1e9).astype(int)
    df['month'] = df['month'].astype(str)

    return df

def get_hourly_activity_plot(df):

    fig = px.bar(df['hour'].value_counts(normalize=True).sort_index().reset_index()\
                 .rename(columns={'hour': '% of Activity',
                                  'index': 'Hour of day'}),
                 x="Hour of day", y="% of Activity", title='n_message')
    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(paper_bgcolor="rgba(255,255,255,0.5)", plot_bgcolor="rgba(255,255,255,0.5)")

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def plot_monthly_activity_plot(df):
    fig = px.line(df.groupby('month', as_index=False).agg(n_message=('username', 'count')),
                  x="month", y="n_message", title='messages count over time')
    fig.update_layout(paper_bgcolor="rgba(255,255,255,0.5)", plot_bgcolor="rgba(255,255,255,0.5)")
                      #,height=900, width=1200)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



def plot_user_message_responses_flow(df, n_users=5):
    fig = FigureBuilder(chat=WhatsAppChat(
        df[df['username'].isin(df['username'].value_counts()[0: n_users].index)])).user_message_responses_flow()
    fig.update_layout(paper_bgcolor="rgba(255,255,255,0.5)", plot_bgcolor="rgba(255,255,255,0.5)",
                      height=900, width=1200)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_locations_markers(df):
    locations_df = df[df['message'].str.contains('maps.google')]
    if not locations_df.empty:
        locations_df['lat'], locations_df['lon'] = zip(*locations_df['message'].str.extract(URL_PATTERN)[0]\
                                                       .apply(lambda x: x.split('=')[1].split(',')))

        relevant_indexes = [list(locations_df.index),
                            list(locations_df.index + 1),
                            list(locations_df.index - 1)]

        loc_df = df.drop(['hour', 'date', 'month', 'year'], axis=1) \
            .loc[set().union(*relevant_indexes)].sort_index() \
            .merge(pd.DataFrame(zip(*relevant_indexes),
                                index=list(locations_df.index)) \
                   .melt(ignore_index=False).reset_index() \
                       [['index', 'value']], left_index=True, right_on='value') \
            .drop('value', axis=1)

        html_list = []
        for index, temp_df in loc_df.groupby('index'):
            html_list.append({'index': index, "popup": temp_df[['username', 'timestamp', 'message']].to_html(index=False)})
        locations_df = locations_df.merge(pd.DataFrame(html_list), left_index=True, right_on='index')

        return locations_df[['lat', 'lon', 'popup']].to_dict('records')

    else:
        return pd.DataFrame(data=[],columns=['lat', 'lon', 'popup']).to_dict('records')

