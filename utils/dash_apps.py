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
        # ranger_markers = df[['epoch_dt', 'month']].drop_duplicates().set_index('epoch_dt')['month'].to_dict()
        # ranger_markers[]
        app.layout = html.Div([
            html.Div([
            dcc.Dropdown(
                id='username-dropdown',
                options=[{'label': username, 'value': username} for username in df['username'].unique()],
                value=None,
                multi=True,
                style={"width": "93.2%"},
            )]),
            html.Div([
            dcc.RangeSlider(
                id='month-slider',
                allowCross=False,
                value=[df['epoch_dt'].min(), df['epoch_dt'].max()],
                marks=df[['epoch_dt', 'month']].drop_duplicates().set_index('epoch_dt')['month'].to_dict(),
                step=100000,
                verticalHeight=120,
            )], style={"width": "90.2%", "height": "100%"}),

            # dcc.Graph(id='pie-chart', style={'width': '50'}),
            html.Div([
                dcc.Graph(id='totals'),
                dcc.Graph(id='pie-chart'),
            ], style={'display': 'flex', 'flexDirection': 'row'}),


            html.Div([
                dcc.Graph(id='line-chart'),
                dcc.Graph(id='bar-chart'),
            ], style={'display': 'flex', 'flexDirection': 'row'}),
        ])

    @app.callback(
        Output('totals', 'figure'),
        Output('pie-chart', 'figure'),
        Output('line-chart', 'figure'),
        Output('bar-chart', 'figure'),
        [Input('username-dropdown', 'value'),
         Input('month-slider', 'value')]
    )
    def update_plots(selected_username, period):
        df = session.get('data')
        if selected_username:
            filtered_df = df[df['username'].isin(selected_username)]
        else:
            filtered_df = df

        if period:
            s_time, end_time = period
            filtered_df = filtered_df[filtered_df['epoch_dt'].between(s_time, end_time)]

        total_rows = len(filtered_df)
        total_users = filtered_df['username'].nunique()

        monthly_df = filtered_df.groupby('month', as_index=False).agg(n_message=('username', 'count'))

        bar_df = filtered_df['hour'].value_counts(normalize=True).sort_index().reset_index()

        # Pie Chart: Rows per username
        pie_fig = px.pie(filtered_df, names='username', title='Rows per Username')
                    #     height=500, width=700)

        # Line Chart: Number of rows over month
        line_fig = px.line(monthly_df, x='month', y='n_message', title='Number of message over Month')
                         #  height=400, width=700)

        text = f"Total Users: {total_users:,}<br> Total Messages: {total_rows:,}<br> "
        totals_fig = px.scatter_3d().add_annotation(text=text, showarrow=False, font={"size": 30})
                                             #       height=300, width=100)

        # Histogram: Histogram of rows across hour
        hist_fig = px.bar(bar_df \
                          .rename(columns={'hour': '% of Activity',
                                           'index': 'Hour of day'}),
                          x="Hour of day", y="% of Activity", title='Histogram of Rows across Hour')
                          #height=400, width=700)
        hist_fig.layout.yaxis.tickformat = ',.1%'
        hist_fig.update_xaxes(tickangle=60)

        for fig in [pie_fig, line_fig, hist_fig, totals_fig]:
            fig.update_layout(paper_bgcolor="rgba(255,255,255,0.1)", plot_bgcolor="rgba(255,255,255,0.1)",
                              xaxis_rangeslider_visible=True,
                              xaxis_rangeslider_thickness=0.04)

        return totals_fig, pie_fig, line_fig, hist_fig

    return app
