import pandas as pd
from whatstk import WhatsAppChat
from whatstk.graph import plot, FigureBuilder
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
