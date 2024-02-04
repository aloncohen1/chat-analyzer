import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from whatstk import WhatsAppChat
from whatstk.graph import FigureBuilder

DAYS_ORDER_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAYS_ORDER_HE = ["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAYS_HEB_DICT = {"Monday":"שני", "Tuesday":"שלישי", "Wednesday":"רביעי",
                 "Thursday":"חמישי", "Friday":"שישי", "Saturday":"שבת", "Sunday":"ראשון"}
DAYS_ORDER_LANG_DICT = {'en': DAYS_ORDER_EN, 'he': DAYS_ORDER_HE}

OTHER_DICT = {'en': "Other", "he": "אחר"}

INTERACTION_NOTE_DICT = {'en': 'A response from user X to user Y happens if user X sends a message right after a message from user Y',
                         'he': "'תגובה ממשתמש א' למשתמש ב' מתרחשת אם משתמש א' שלח הודעה מיד לאחר הודעה ממשתמש ב"}

HOURS_ORDER = pd.date_range('1970-01-01', '1970-01-02', freq='H').strftime("%H:%M")

FREQ_DICT = {'date': '1D', 'month': 'MS', 'week': 'W-MON'}
def generate_geo_barchart(df, language='en', geo_key='city', top_n=10):

    xaxis_lang_dict = {'en': '% of Locations', 'he': 'אחוז מיקומים'}

    agg_df = df[geo_key].value_counts(normalize=True).reset_index()[0:top_n] \
        .rename(columns={'index': geo_key.capitalize(), geo_key: xaxis_lang_dict[language]}) \

    agg_df = agg_df.append(pd.DataFrame(data=[[1 - agg_df[xaxis_lang_dict[language]].sum(), OTHER_DICT[language]]],
                                        columns=[xaxis_lang_dict[language], geo_key.capitalize()]))\
        .sort_values(xaxis_lang_dict[language])

    fig = px.bar(agg_df, x=xaxis_lang_dict[language], y=geo_key.capitalize(), orientation='h')
    fig.update_traces(marker_color="#24d366")
    fig.layout.xaxis.tickformat = ',.1%'

    return fig

def generate_geo_piehart(df, language='en',top_n=10):

    geo_key = "country"

    title_lang_dict = {'en': 'Country Share by Locations', "he": "אחוז מיקומים פר מדינה"}

    agg_df = df[geo_key].value_counts(normalize=True).reset_index()[0:top_n] \
        .rename(columns={'index': 'Area'})

    agg_df = agg_df.append(pd.DataFrame(data=[[1 - agg_df[geo_key].sum(), OTHER_DICT[language]]], columns=[geo_key, "Area"]))
    agg_df[f'% of {geo_key}'] = agg_df[geo_key].apply(lambda x: "{0:.1f}%".format(x * 100))
    fig = px.pie(agg_df, values=geo_key, names='Area', hole=0.5, hover_data=[f'% of {geo_key}'])

    fig.update_traces(marker=dict(line=dict(color='black', width=2)),
                      title_text=title_lang_dict[language])
    fig.update_traces(showlegend=False, textposition='inside', textinfo='percent+label')
    fig.update_traces(hovertemplate=geo_key.capitalize() + ": %{label}<br>% of Locations: %{percent}")
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig


def generate_piechart(df, language='en', top_n=10):
    if not df.empty:
        username_text = {'en': 'Username', 'he': "משתמש"}
        other_text = {'en': 'Other', 'he': 'אחר'}
        messages_text = {'en': '% of Messages', 'he': "הודעות %"}
        plot_title = {'en': 'Messages Share by Username', 'he': "אחוז הודעות לפי משתמש"}

        top_n = min(top_n, df["username"].nunique())

        agg_df = df["username"].value_counts(normalize=True)[0:top_n].reset_index()

        agg_df = agg_df.append(pd.DataFrame(data=[[1-agg_df["username"].sum(), other_text[language]]],
                                            columns=["username", "index"]))\
            .rename(columns={'index': username_text[language]})

        agg_df[messages_text[language]] = agg_df['username'].apply(lambda x: "{0:.1f}%".format(x * 100))

        fig = px.pie(agg_df, values="username", names=username_text[language], hole=0.5, hover_data=[messages_text[language]])
        # color_discrete_map={"Other": 'rgb(36, 211, 102)'}

        fig.update_traces(marker=dict(line=dict(color='black', width=2)), title_text=plot_title[language])
        fig.update_traces(showlegend=False, textposition='inside', textinfo='percent+label')
        fig.update_traces(hovertemplate="Username: %{label}<br>% of Messages : %{percent}")
        fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

        return fig

    else:
        return go.Figure()

def generate_activity_overtime(df, min_date, max_date, language='en', unit='Messages', granularity='month'):

    unit_dict = {'Messages': 'count', 'Users': 'nunique'}
    unit_lan_dict = {"he": {'Messages': 'הודעות', 'Users': 'משתמשים'},
                     "en": {'Messages': 'Messages', 'Users': 'Users'}}
    granularity_lan_dict = {"he": {'month': 'חודש', 'week': 'שבוע', 'date': 'יום'},
                            'en': {'month': 'month', 'week': 'week', 'date': 'day'}}

    plot_title = {'en': 'Overall Chat Activity Over Time', 'he': "טרנד פעילות כללית על פני זמן"}

    agg_df = df.groupby(granularity).agg({'username': unit_dict[unit]}) \
        .reindex(pd.date_range(min_date, max_date, freq=FREQ_DICT[granularity]), fill_value=0).reset_index() \
        .rename(columns={'username': f'# {unit_lan_dict[language][unit]}', 'index': granularity_lan_dict[language][granularity].capitalize()})

    fig = px.line(agg_df, x=granularity_lan_dict[language][granularity].capitalize(),
                  y=f'# {unit_lan_dict[language][unit]}')
    fig['data'][0]['line']['color'] = "#24d366"
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)", hovermode="x",
                      title_text=plot_title[language])
    fig.update_traces(mode='markers+lines')
    return fig

def generate_users_activity_overtime(df, min_date, max_date, language='en', granularity='month',top_n=5):
    if not df.empty:
        granularity_lan_dict = {"he": {'month': 'חודש', 'week': 'שבוע', 'date': 'יום'},
                                'en': {'month': 'month', 'week': 'week', 'date': 'day'}}
        messages_lang_dict = {'en': '# of Messages', 'he': "# הודעות"}
        username_lang_dict = {'en': 'Username', 'he': "משתמש"}
        plot_title = {'en': 'Users Activity Over Time (Top %s)', 'he': "(Top %s) טרנד פעילות משתמשים על פני זמן"}

        top_n = min(top_n, df["username"].nunique())

        users_dfs = []

        users = df["username"].value_counts(normalize=True)[0:top_n].index

        for user in users:
            user_df = df[df['username'] == user].groupby([granularity]) \
                .agg(n_messages=('username', "count")) \
                .reindex(pd.date_range(min_date, max_date, freq=FREQ_DICT[granularity]), fill_value=0).reset_index()
            user_df['username'] = user
            users_dfs.append(user_df)

        agg_df = pd.concat(users_dfs, ignore_index=True)\
            .rename(columns={'n_messages': messages_lang_dict[language],
                             'index': granularity_lan_dict[language][granularity].capitalize(),
                             'username': username_lang_dict[language]})

        fig = px.line(agg_df, x=granularity_lan_dict[language][granularity].capitalize(), y=messages_lang_dict[language],
                      color=username_lang_dict[language])

        fig.update_layout(title_text=plot_title[language] % top_n)# f'Users Activity Over Time (Top {top_n})')
        fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")
        fig.update_layout(hovermode="x") # legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
        fig.update_traces(mode='markers+lines')
        return fig
    else:
        return go.Figure()

def generate_hourly_activity(df, language='en'):

    xaxis_lang_dict = {'en': "Hour of day", 'he': "שעה"}
    yaxis_lang_dict = {'en': "% of Activity", 'he': "פעילות %"}
    title_lang_dict = {'en': 'Activity by Hour of Day', 'he': "פעילות לפי שעה ביום"}

    fig = px.bar(df['hour'].value_counts(normalize=True).sort_index().reset_index()\
                 .rename(columns={'hour': yaxis_lang_dict[language],
                                  'index': xaxis_lang_dict[language]}),
                 x=xaxis_lang_dict[language], y=yaxis_lang_dict[language])

    fig.update_traces(marker_color="#24d366")

    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(title_text=title_lang_dict[language])
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig


def generate_day_of_week_activity(df, language='en'):

    yaxis_lang_dict = {'en': "Day of Week", 'he': "יום"}
    xaxis_lang_dict = {'en': "% of Activity", 'he': "פעילות %"}
    title_lang_dict = {'en': 'Activity by Day of Week', 'he': "פעילות לפי יום בשבוע"}

    agg_df = df['day_name'].value_counts(normalize=True)

    missing_days = set(DAYS_ORDER_EN) - set(agg_df.index)
    if len(missing_days) > 0:
        agg_df = pd.concat([agg_df, pd.Series(data=[0]*len(missing_days), index=missing_days, name='day_name')])

    agg_df = agg_df[DAYS_ORDER_LANG_DICT[language]].reset_index()
    if language == 'he':
        agg_df['index'] = agg_df['index'].map(DAYS_HEB_DICT)
    fig = px.bar(agg_df.rename(columns={'day_name': xaxis_lang_dict[language], 'index': yaxis_lang_dict[language]}),
                 x=yaxis_lang_dict[language], y=xaxis_lang_dict[language])

    fig.update_traces(marker_color="#24d366")

    fig.layout.yaxis.tickformat = ',.1%'
    fig.update_xaxes(tickangle=60)
    fig.update_layout(title_text=title_lang_dict[language])
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig


def generate_activity_matrix(df, language='en'):

    xaxis_lang_dict = {'en': "Hour", 'he': "שעה"}
    yaxis_lang_dict = {'en': "Day", 'he': "יום"}
    title_lang_dict = {'en': 'Message Distribution by Day and Hour', 'he': "התפלגות הפעילות על פני ימים ושעות"}

    matrix_df = df.groupby(['day_name', 'hour'], as_index=False).agg(n_message=('username', 'count')) \
        .rename(columns={'day_name': 'Day',
                         'hour': 'Hour'})\
        .pivot(index='Day', columns='Hour', values='n_message') / len(df)

    matrix_df = matrix_df.reindex(DAYS_ORDER_LANG_DICT[language])
    if language=='he':
        matrix_df.index = matrix_df.index.map(DAYS_HEB_DICT)
    for col in HOURS_ORDER:
        if col not in matrix_df:
            matrix_df[col] = 0
    matrix_df = matrix_df[HOURS_ORDER].fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=matrix_df.values,
        x=matrix_df.columns,
        y=matrix_df.index,
        colorscale=[[0, "#ffffff"], [1, '#24d366']], showscale=False,
        hovertemplate="Day: %{y}<br>Hour: %{x}<br>% of Messages: %{z:.2%}",
        name=""))

    fig.update_layout(title=title_lang_dict[language], xaxis_title=xaxis_lang_dict[language],
                      yaxis_title=yaxis_lang_dict[language], coloraxis_showscale=False)

    return fig


def generate_message_responses_flow(df, language='en', n_users=5):

    title_lang_dict = {'en': f'Message flow (Top {n_users})', 'he': f'איטראקציית משתמשים (טופ {n_users})'}

    fig = FigureBuilder(chat=WhatsAppChat(
        df[df['username'].isin(df['username'].value_counts()[0: n_users].index)]))\
        .user_message_responses_flow(title_lang_dict[language])
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")
    fig.add_annotation(showarrow=False, text=INTERACTION_NOTE_DICT[language], font=dict(size=10),
                       xref='x domain', x=0, yref='y domain', y=-0.3)
    return fig


def user_message_responses_heatmap(df, language='en', n_users=10):

    title_lang_dict = {'en': f'Message flow (Top {n_users})', 'he': f'אניטראקציית משתמשים (טופ {n_users})'}
    xaxis_lang_dict = {'en': 'Receiver', 'he': 'נמען'}
    yaxis_lang_dict = {'en': 'Sender', 'he': 'מען'}

    fig = FigureBuilder(chat=WhatsAppChat(
        df[df['username'].isin(df['username'].value_counts()[0: n_users].index)]))\
        .user_message_responses_heatmap(title=title_lang_dict[language])
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)", )
    fig.update_traces(name="", hovertemplate="Day: %{y}---> %{x}:  %{z:,}")
    fig.add_annotation(showarrow=False, text=INTERACTION_NOTE_DICT[language], font=dict(size=10), xref='x domain',
                       x=-0.24, yref='y domain', y=-0.55)

    fig.update_layout(xaxis_title=xaxis_lang_dict[language], yaxis_title=yaxis_lang_dict[language])

    return fig


def generate_sentiment_piehart(df,colors_mapping):

    agg_df = df["label"].value_counts(normalize=True).reset_index()

    agg_df['percent'] = agg_df['label'].apply(lambda x: "{0:.1f}%".format(x * 100))

    fig = px.pie(agg_df, values="label", names='index', color='index', hole=0.5,
                 hover_data=["index", "percent"], color_discrete_map=colors_mapping)

    fig.update_traces(title_text='Overall Sentiments')
    fig.update_traces(showlegend=False, textposition='inside', textinfo='percent+label')
    fig.update_traces(hovertemplate="Label: %{label}<br>Value : %{percent}")
    fig.update_layout(paper_bgcolor="rgba(18,32,43)", plot_bgcolor="rgba(18,32,43)")

    return fig

def generate_sentiment_bars(df, colors_mapping):

    agg_df = df.groupby(['week', 'label'], as_index=False).agg(n_messages=('sent','count'))

    agg_df['messages_pct'] = agg_df['n_messages'] / agg_df['n_messages'].sum()
    agg_df['messages_pct_text'] = agg_df['messages_pct'].apply(lambda x: "{0:.1f}%".format(x * 100))

    fig = px.bar(agg_df, x="week", y="messages_pct", hover_data=['messages_pct_text'],custom_data=['messages_pct_text'],
                 color="label", title="Sentiment Over Time", color_discrete_map=colors_mapping)

    fig.update_traces(hovertemplate="Label: %{label}<br>Value : %{customdata[0]}")
    fig.update_layout(yaxis_tickformat='.0%')

    return fig