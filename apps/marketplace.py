import dash
from dash import html
import requests
import pandas as pd
import json
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app


# convert snake case variables to readable text with capitalized letter
def convert_snake(snake_case):
    return snake_case.replace("_", " ").title()


# Variables
CAMERAS = [
    "CAM_FRONT",
    "CAM_BACK",
    "CAM_FRONT_ZOOMED",
    "CAM_FRONT_LEFT",
    "CAM_FRONT_RIGHT",
    "CAM_BACK_RIGHT",
    "CAM_BACK_LEFT",
]
LIDARS = ["LIDAR_TOP", "LIDAR_FRONT_RIGHT", "LIDAR_FRONT_LEFT"]
# sale_price param does not work on query - status 500 internal service error
order_by = ['token_id', 'sale_date', 'sale_count']

controls = [
    dbc.FormGroup(
        [
            dbc.Label("Collection"),
            dbc.Select(
                id="camera",
                options=[
                    {"label": convert_snake(s.replace("CAM_", "")), "value": s}
                    for s in CAMERAS
                ],
                value=CAMERAS[0],
            ),
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Sort by"),
            dbc.Select(
                id="order_by",
                value=order_by[0],
                options=[
                    {"label": convert_snake(s), "value": s}
                    for s in order_by
                ],
            ),
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Order"),
            dbc.RadioItems(
                options=[
                    {"label": "desc", "value": 1},
                    {"label": "asc", "value": 2},
                ],
                value=1,
                id="radioitems-input",
            ),
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Spinner(
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "apply", id="apply", n_clicks=0, color="dark"
                        ),
                        dbc.Button("reset", id="reset", n_clicks=0, color="dark", outline=True),
                    ],
                    id="button-group1",
                    style={"width": "50%"},
                    vertical=True,
                ),
                spinner_style={"margin-top": 0, "margin-bottom": 0},
            ),
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Page"),
            html.Br(),
            dbc.Spinner(
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "Prev", id="prev", n_clicks=0, color="dark", outline=True
                        ),
                        dbc.Button("Next", id="next", n_clicks=0, color="dark", outline=True),
                    ],
                    id="button-group",
                    style={"width": "50%"},
                ),
                spinner_style={"margin-top": 0, "margin-bottom": 0},
            ),
        ]
    ),
]

###################################################################################################
collection = []
order_by = ['token_id', 'sale_date', 'sale_count']  # order_by sale_price is broken in the api for some reason


# convert snake case variables to readable text with capitalized letter
def convert_snake(snake_case):
    return snake_case.replace("_", " ").title()


def get_assets():
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"order_direction": "desc", "offset": 0, "limit": "30"}  # .format(offset=offset)
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    # df_collection = pd.json_normalize(df['assets']['collection'])
    col_list = ['id', 'token_id', 'name', 'image_url', 'collection.name', 'last_sale.total_price', 'asset_contract.address']
    df = pd.DataFrame(df, columns=col_list)
    # print(df_collection)
    # print(df)
    return df


def create_card(card_img, card_collection, card_title, card_price, token_id, asset_contract_address):
    asset_link = dbc.CardLink("{name}".format(name=card_title),
                              href="/asset?asset_contract_address={address}&token_id={token_id}".format(
                                  address=asset_contract_address, token_id=token_id))
    return dbc.Card(
        [
            dbc.CardImg(src=card_img, top=True),
            dbc.CardBody(
                [
                    html.H4(asset_link, className="card-title"),
                    html.P(card_collection, className="card-collection"),
                    html.P(card_price, className="card-price"),
                ],
                className="asset_cardbody",
            ),
        ],
        color="dark",
        inverse=True,
        className="asset_card"
    )


def create_cardgrid(data):
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['name'][item], data['collection.name'][item], data['last_sale.total_price'][item], data['token_id'][item], data['asset_contract.address'][item]))
    return dbc.CardColumns(cards)


def create_layout(app):
    data = get_assets()
    return html.Div(
        children=[
            # HEADER
            html.Div(
                children=[
                    html.H1('NFT', id='header-text'),
                ],
                className="header",
            ),
            # CONTENT
            dbc.Card(dbc.Row([dbc.Col(c) for c in controls], form=True), body=True),
            html.Div(id="content"),
            create_cardgrid(data),
        ],
        className="main"
    )


#@app.callback()
#def update_grid():
#    assets = get_assets(order_by, order_direction, offset, collection)
#    create_cardgrid(assets)


