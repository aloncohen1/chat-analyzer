import pandas as pd
from whatstk import WhatsAppChat
import streamlit as st
from whatstk.graph import FigureBuilder
from streamlit_extras.switch_page_button import switch_page
import json
import plotly
import pygeohash as pgh
import numpy as np

URL_PATTERN = r"(https:\/\/maps\.google\.com\/\?q=-?\d+\.\d+,-?\d+\.\d+)"


def local_css(file_name):
    with open(file_name) as f:
        return '<style>{}</style>'.format(f.read())


def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "WhatsappAnalyzer";
                font-family: sans-serif;
                margin-left: 20px;
                margin-top: -300%;
                font-size: 30px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def refer_to_load_data_section():
    st.title("Please Upload Data to Analyze")
    upload_data = st.button("Take me to uploading data page!")
    if upload_data:
        switch_page("home")


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
    df['week'] = df['timestamp'].dt.to_period('W').dt.start_time
    df['month'] = df['timestamp'].to_numpy().astype('datetime64[M]')
    df['day_name'] = df['timestamp'].dt.day_name()

    return df

def add_filters():
    min_date = st.session_state['data']['date'].min()
    max_date = st.session_state['data']['date'].max()

    st.sidebar.write('')
    time_filter = st.sidebar.slider("Time Period", min_date, max_date, (min_date, max_date))

    st.sidebar.write('')

    users_filter = st.sidebar.multiselect("Users", ["All"] + list(st.session_state['data']['username'].unique()),
                                          default='All')
    if "All" in users_filter or not users_filter:
        filtered_df = st.session_state['data']
    else:
        filtered_df = st.session_state['data'][st.session_state['data']['username'].isin(users_filter)]

    return filtered_df[filtered_df['date'].between(time_filter[0], time_filter[1])]

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

        locations_df['lat'], locations_df['lon'] = locations_df['lat'].astype(float), locations_df['lon'].astype(float)

        relevant_indexes = [list(locations_df.index),
                            list(locations_df.index + 1),
                            list(locations_df.index - 1)]

        loc_df = st.session_state['data'].drop(['hour', 'date', 'month', 'year'], axis=1) \
            .loc[set().union(*relevant_indexes)].sort_index() \
            .merge(pd.DataFrame(zip(*relevant_indexes),
                                index=list(locations_df.index))\
                   .melt(ignore_index=False).reset_index()\
                       [['index', 'value']], left_index=True, right_on='value').drop('value', axis=1)

        html_list = []
        for index, temp_df in loc_df.groupby('index'):
            html_list.append({'index': index, "popup": temp_df[['username', 'timestamp', 'message']].to_html(index=False)})
        locations_df = locations_df.merge(pd.DataFrame(html_list), left_index=True, right_on='index')
        locations_df['geohash'] = locations_df.apply(lambda x: pgh.encode(x['lat'], x['lon'], precision=4), axis=1)

        return locations_df[['lat', 'lon', 'popup', 'username', 'timestamp', 'geohash']]

    else:
        return locations_df

