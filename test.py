import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import os
import plotly.express as px
from whatstk import df_from_txt_whatsapp
from utils.whtasup_utils import add_timestamps_df

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create a directory to store data files
if not os.path.exists('data'):
    os.makedirs('data')

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Link(
            rel='stylesheet',
            href='/assets/styles.css'  # Link to your external stylesheet
        ),
        dbc.Row([
            dbc.Col(id='page-content', width=12),
        ]),
    ]),
])

# Upload page layout
upload_layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload Data File'),
        multiple=False
    ),
    html.Div(id='uploaded-data')
])

# Main page layout with sections
main_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Nav(
                [
                    dbc.NavLink("Main", href="/tab-main"),
                    dbc.NavLink("Section A", href="/tab-section-a"),
                    dbc.NavLink("Section B", href="/tab-section-b"),
                    dbc.NavLink("Section C", href="/tab-section-c"),
                ],
                vertical=True,
                pills=True,
                className='sidebar'
            ),
            width=3
        ),
        dbc.Col([
            dcc.RangeSlider(
                id='date-range-slider',
                marks={i: str(i) for i in range(1, 32)},
                min=1,
                max=31,
                value=[1, 31]
            ),
            dcc.Dropdown(
                id='username-dropdown',
                multi=True
            ),
            dbc.Col(id='tabs-content'),
        ], width=9)
    ])
], className='main-container')


# Callback to update the layout based on the URL pathname
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def display_page(pathname):
    if pathname == '/':
        return upload_layout
    elif pathname == '/tab-main':
        return main_layout

# Callback to upload and display data
@app.callback(
    Output('uploaded-data', 'children'),
    Output('url', 'pathname'),
    Input('upload-data', 'contents'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def upload_data(contents, current_path):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')

    # Save the uploaded data to a file
    with open('data/uploaded_data.txt', 'w') as f:
        f.write(decoded)

    # Redirect to the main page after data upload
    return f'Data uploaded', '/tab-main'

if __name__ == '__main__':
    app.run_server(debug=True)
