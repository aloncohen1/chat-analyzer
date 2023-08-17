import pandas as pd
from whatstk import WhatsAppChat
from whatstk.graph import FigureBuilder
import plotly.graph_objects as go
import plotly.express as px
import plotly
import json
from random import choice
import numpy as np

URL_PATTERN = r"(https:\/\/maps\.google\.com\/\?q=-?\d+\.\d+,-?\d+\.\d+)"

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_string(n):
    return ''.join([choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(n)]).encode()


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


def plot_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    align='left'),
        cells=dict(values=[df[i].astype(str) for i in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(paper_bgcolor="rgba(255,255,255,0.5)", plot_bgcolor="rgba(255,255,255,0.5)",
                      height=900, width=1200)
    fig = add_filter_to_fig(fig, df, ['username', 'year', 'month'])
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def add_filter_to_fig(fig,df, filters=['username']):
    fig.update_layout(
        updatemenus=[
            {
                "y": 1 - (i / 15),
                "buttons": [
                    {
                        "label": c,
                        "method": "restyle",
                        "args": [
                            {
                                "cells": {
                                    "values": df.T.values
                                    if c == f"All ({menu})"
                                    else df.loc[df[menu].eq(c)].T.values
                                }
                            }
                        ],
                    }
                    for c in [f"All ({menu})"] + df[menu].astype(str).unique().tolist()
                ],
            }
            for i, menu in enumerate(filters)
        ]
    )
    return fig