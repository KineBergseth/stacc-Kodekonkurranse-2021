import dash
from dash import html
import requests
import pandas as pd
import json
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

collections = ['', 'dotdotdots', 'bears-deluxe', 'sappy-seals', 'gutterpigeons', 'epiceagles', 'infinity-frogs-nft']
# sale_price param does not work on query - status 500 internal service error
order_by_list = ['pk', 'sale_date', 'sale_count']


# convert snake case variables to readable text with capitalized letter
def convert_snake(snake_case):
    return snake_case.replace("_", " ").title()


controls = [
    html.Div(
        [
            dbc.Label("Collection"),
            dbc.Select(
                id="collection-input",
                options=[
                    {"label": convert_snake(c), "value": c}
                    for c in collections
                ],
                value=collections[0],
            ),
        ]
    ),
    html.Div(
        [
            dbc.Label("Sort by"),
            dbc.Select(
                id="order-by-input",
                value=order_by_list[0],
                options=[
                    {"label": convert_snake(o), "value": o}
                    for o in order_by_list
                ],
            ),
        ]
    ),
    html.Div(
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
    html.Div(
        [
            dbc.Label("Page"),
            html.Br(),
            dbc.Pagination(max_value=5, first_last=True, active_page=1, id="asset_pagination"),
        ]
    ),
]


def get_assets(order_by, order_direction, offset, limit, collection):
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"order_by": f"{order_by}", "order_direction": f"{order_direction}", "offset": f"{offset}",
                   "limit": f"{limit}", "collection": f"{collection}"}
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
        className="asset_card col"
    )


def create_cardgrid(data):
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['name'][item], data['collection.name'][item],
                                 data['last_sale.total_price'][item], data['token_id'][item],
                                 data['asset_contract.address'][item]))
    return html.Div(cards, className="row row-cols-4")


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
            dbc.Card(dbc.Row([dbc.Col(c) for c in controls]), body=True),
            html.Div(id="content"),
        ],
        className="main"
    )


@app.callback(
    Output("content", "children"),
    [Input("collection-input", "value"),
     Input("order-by-input", "value"),
     Input("order-direction-input", "value"),
     Input("asset_pagination", "active_page")]
    # page no.
)
def update_grid(collection, order_by, order_direction, page_no):
    limit = 20
    page_no = page_no
    offset = (page_no * limit) - limit
    #collection = ""
    assets = get_assets(order_by, order_direction, offset, limit, collection)
    return create_cardgrid(assets)
