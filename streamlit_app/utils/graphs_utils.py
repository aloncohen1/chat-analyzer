import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from whatstk import WhatsAppChat
from whatstk.graph import FigureBuilder

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

HOURS_ORDER = pd.date_range('1970-01-01', '1970-01-02', freq='H').strftime("%H:%M")


def generate_geo_chart(df, geo_key='state_district'):

    agg_df = df[geo_key].value_counts(normalize=True).reset_index()\
        .rename(columns={'index': 'Area'})
    agg_df[f'% of locations'] = agg_df[geo_key].apply(lambda x: "{0:.1f}%".format(x * 100))
    fig = px.bar(agg_df, y="Area", x=geo_key, orientation='h')
    fig.update_traces(marker_color="#24d366")
    fig.layout.xaxis.tickformat = ',.1%'

    return fig


def generate_piechart(df, top_n=10, metric="Messages"):

    top_n = min(top_n, df["username"].nunique())

    agg_df = df["username"].value_counts(normalize=True)[0:top_n].reset_index()

    agg_df = agg_df.append(pd.DataFrame(data=[[1-agg_df["username"].sum(), 'Other']],
                                        columns=["username", "index"]))\
        .rename(columns={'index': 'Username'})

    agg_df[f'% of {metric}'] = agg_df['username'].apply(lambda x: "{0:.1f}%".format(x * 100))

    fig = px.pie(agg_df, values="username", names='Username', hole=0.5, hover_data=[f'% of {metric}'])
    # color_discrete_map={"Other": 'rgb(36, 211, 102)'}

    fig.update_traces(marker=dict(line=dict(color='black', width=2)), title_text=f'{metric} Share by Username')
    fig.update_traces(showlegend=False, textposition='inside', textinfo='percent+label')
    fig.update_traces(hovertemplate="Username: %{label}<br>% of "+metric+" : %{percent}")
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig


def generate_activity_overtime(df, min_date, max_date, granularity='month'):

    freq_dict = {'date': '1D', 'month': 'MS', 'week': 'W-MON'}

    agg_df = df.groupby(granularity).agg({'username': 'count'}) \
        .reindex(pd.date_range(min_date, max_date, freq=freq_dict[granularity]), fill_value=0).reset_index() \
        .rename(columns={'username': '# of Messages', 'index': granularity.capitalize()})

    fig = px.line(agg_df, x=granularity.capitalize(), y='# of Messages')
    fig['data'][0]['line']['color'] = "#24d366"
    fig.update_layout(title_text='Chat Activity Over Time')
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")
    fig.update_layout(hovermode="x")
    fig.update_traces(mode='markers+lines')
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

    agg_df = df['day_name'].value_counts(normalize=True)

    missing_days = set(DAYS_ORDER) - set(agg_df.index)
    if len(missing_days) > 0:
        agg_df = pd.concat([agg_df, pd.Series(data=[0]*len(missing_days),
                                             index=missing_days, name='day_name')])

    fig = px.bar(agg_df[DAYS_ORDER].reset_index()\
                 .rename(columns={'day_name': '% of Activity',
                                  'index': 'Day of Week'}),
                 x="Day of Week", y="% of Activity")

    fig.update_traces(marker_color="#24d366")

    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(title_text='Activity by Day of Week')
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig


def generate_activity_matrix(df):

    matrix_df = df.groupby(['day_name', 'hour'], as_index=False).agg(n_message=('username', 'count')) \
        .rename(columns={'day_name': 'Day',
                         'hour': 'Hour'})\
        .pivot(index='Day', columns='Hour', values='n_message').fillna(0).reindex(DAYS_ORDER) / len(df)

    fig = go.Figure(data=go.Heatmap(
        z=matrix_df.values,
        x=matrix_df.columns,
        y=matrix_df.index,
        colorscale=[[0, "#ffffff"], [1, '#24d366']], showscale=False,
        hovertemplate="Day: %{y}<br>Hour: %{x}<br>% of Messages: %{z:.2%}",
        name=""))

    fig.update_layout(title='Message Distribution by Day and Hour',
                      xaxis_title='Hour', yaxis_title='Day', coloraxis_showscale=False)

    return fig

def generate_message_responses_flow(df, n_users=7):
    fig = FigureBuilder(chat=WhatsAppChat(
        df[df['username'].isin(df['username'].value_counts()[0: n_users].index)])).user_message_responses_flow()
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")
    # fig.update_layout(paper_bgcolor="rgba(255,255,255,0.5)", plot_bgcolor="rgba(255,255,255,0.5)",
    #                   height=900, width=1200)
    return fig