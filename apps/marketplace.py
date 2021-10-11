import dash
from dash import html
import requests
import pandas as pd
import json
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app



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

# collection = []
# sale_price param does not work on query - status 500 internal service error
order_by_list = ['pk', 'sale_date', 'sale_count']


# convert snake case variables to readable text with capitalized letter
def convert_snake(snake_case):
    return snake_case.replace("_", " ").title()

controls = [
    dbc.FormGroup(
        [
            dbc.Label("Collection"),
            dbc.Select(
                id="collection-input",
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
                id="order-by-input",
                value=order_by_list[0],
                options=[
                    {"label": convert_snake(s), "value": s}
                    for s in order_by_list
                ],
            ),
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Order"),
            dbc.RadioItems(
                options=[
                    {"label": "desc", "value": "desc"},
                    {"label": "asc", "value": "asc"},
                ],
                value="desc",
                id="order-direction-input",
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






def get_assets(order_by, order_direction, offset, limit):
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"order_by": f"{order_by}", "order_direction": f"{order_direction}", "offset": f"{offset}",
                   "limit": f"{limit}"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    col_list = ['id', 'token_id', 'name', 'image_url', 'collection.name', 'last_sale.total_price',
                'asset_contract.address']
    df = pd.DataFrame(df, columns=col_list)
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
        cards.append(create_card(data['image_url'][item], data['name'][item], data['collection.name'][item],
                                 data['last_sale.total_price'][item], data['token_id'][item],
                                 data['asset_contract.address'][item]))
    return dbc.CardColumns(cards)


def create_layout(app):
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
        ],
        className="main"
    )


@app.callback(
    Output("content", "children"),
    [Input("collection-input", "value"),
     Input("order-by-input", "value"),
     Input("order-direction-input", "value")]
    # page no.
)
def update_grid(collection, order_by, order_direction):
    limit = 3
    page_no = 1
    offset = (page_no * limit) - limit
    collection = ""
    assets = get_assets(order_by, order_direction, offset, limit)
    return create_cardgrid(assets)
