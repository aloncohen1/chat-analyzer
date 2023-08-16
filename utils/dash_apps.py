from flask import session
import dash
from dash import dcc
from dash import html

import plotly.express as px
from dash.dependencies import Input, Output

def table_das_app(server, url_base_pathname='/dash/'):

    app = dash.Dash('app', server=server, url_base_pathname=url_base_pathname)
    app.layout = html.Div()

    @app.server.before_request
    def before_request():

        df = session.get('data')
        app.layout = html.Div([

            dcc.Dropdown(
                id='username-dropdown',
                options=[{'label': username, 'value': username} for username in df['username'].unique()],
                value=None,
                multi=True,
            ),

            # Total rows in df
            html.Div(id='total-rows'),
            dcc.Graph(id='pie-chart',style={'width': '50'}),

            html.Div([
                dcc.Graph(id='line-chart'),
                dcc.Graph(id='bar-chart'),
            ], style={'display': 'flex', 'flexDirection': 'row'}),
        ])

    @app.callback(
        Output('total-rows', 'children'),
        Output('pie-chart', 'figure'),
        Output('line-chart', 'figure'),
        Output('bar-chart', 'figure'),
        [Input('username-dropdown', 'value')]
    )
    def update_plots(selected_username):
        df = session.get('data')
        if selected_username:
            filtered_df = df[df['username'].isin(selected_username)]
        else:
            filtered_df = df

        total_rows = len(filtered_df)

        monthly_df = filtered_df.groupby('month', as_index=False).agg(n_message=('username', 'count'))

        bar_df = filtered_df['hour'].value_counts(normalize=True).sort_index().reset_index()

        # Pie Chart: Rows per username
        pie_fig = px.pie(filtered_df, names='username', title='Rows per Username')

        # Line Chart: Number of rows over month
        line_fig = px.line(monthly_df, x='month', y='n_message', title='Number of message over Month')

        # Histogram: Histogram of rows across hour
        hist_fig = px.bar(bar_df \
                          .rename(columns={'hour': '% of Activity',
                                           'index': 'Hour of day'}),
                          x="Hour of day", y="% of Activity", title='Histogram of Rows across Hour')
        hist_fig.layout.yaxis.tickformat = ',.1%'
        hist_fig.update_xaxes(tickangle=60)

        for fig in [pie_fig, line_fig, hist_fig]:
            fig.update_layout(paper_bgcolor="rgba(255,255,255,0.1)", plot_bgcolor="rgba(255,255,255,0.1)")

        return f"Total rows in df: {total_rows}", pie_fig, line_fig, hist_fig

    return app
