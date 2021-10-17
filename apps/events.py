import dash
import dash_bootstrap_components as dbc
import requests
import pandas as pd
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
from app import app


def get_events(offset, event_type):
    url = f"https://api.opensea.io/api/v1/events?event_type={event_type}&only_opensea=false&offset={offset}&limit=20"
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    df = pd.json_normalize(data['asset_events'])
    df = pd.DataFrame(df)
    # df_orders = pd.json_normalize(data['orders'])
    #print(df)
    #print(df.columns)
    col_list = []
    #df = pd.DataFrame(df, columns=col_list)
    pd.set_option('display.max_colwidth', None)  # extend colwidth to display whole value, instead of partial values
    return df


get_events(0, 'created')


def generate_table(data):
    return dash_table.DataTable(
        id='table',
        data=data.to_dict('records'),
        columns=[
            {"id": "image_url", "name": "NFT", "presentation": "markdown"},
            {"id": "name", "name": "Item"},
            {"id": "price", "name": "Price"},
            {"id": "from", "name": "From"},
            {"id": "to", "name": "To"},
            {"id": "time", "name": "Time"},
        ],
        markdown_options={"html": True},
        sort_action='native',
        style_header={},
        style_cell={'textAlign': 'left', "whiteSpace": "pre-line"},
        style_as_list_view=True,
        editable=False,
        row_deletable=True,
    )


def create_layout():
    """
    Creates the layout for the home page
    :return: layout with all the elements in
    """

    return html.Div(
        children=[
            html.Div(
                [
                    html.H1('Activity', id='header-text text-center'),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Listings", id="listings", outline=True, color="primary"),
                            dbc.Button("Sales", id="sales", outline=True, color="primary"),
                            dbc.Button("Bids", id="bids", outline=True, color="primary"),
                            dbc.Button("Transfers", id="transfers", outline=True, color="primary"),
                        ]
                    )
                ],
                className="header",
            ),

        ],
        className="main"
    )
