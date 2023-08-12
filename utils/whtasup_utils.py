import pandas as pd
from whatstk import WhatsAppChat
from whatstk.graph import FigureBuilder
import plotly.graph_objects as go
import plotly.express as px
import plotly
import json



def add_timestamps_df(df):

    df['timestamp'] = pd.to_datetime(df['date'])
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date
    df['month'] = df.timestamp.dt.to_period('M').dt.to_timestamp()

    return df

def get_hourly_activity(df):

    return df.groupby('hour', as_index=False).agg(n_message=('username', 'count'))

def plot_monthly_activity(df):
    fig = px.line(df.groupby('month', as_index=False).agg(n_message=('username', 'count')),
                  x="month", y="n_message", title='messages count over time')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



def plot_user_message_responses_flow(df, n_users=5):
    fig = FigureBuilder(chat=WhatsAppChat(
        df[df['username'].isin(df['username'].value_counts()[0: n_users].index)])).user_message_responses_flow()
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_locations_markers(df):
    locations_df = df[df['message'].str.contains('location:')]
    locations_df['lat'], locations_df['lon'] = zip(*locations_df['message'].apply(lambda x: x.split('=')[1].split(',')))
    locations_df['popup'] = locations_df['username'] + ': ' + locations_df['timestamp'].astype(str)

    return locations_df[['lat', 'lon', 'popup']].to_dict('records')


def plot_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    # fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[i].astype(str) for i in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig = add_filter_to_fig(fig,df,['username','month'])
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def add_filter_to_fig(fig,df, filters=['username']):
    fig.update_layout(
        updatemenus=[
            {
                "y": 1 - (i / 5),
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