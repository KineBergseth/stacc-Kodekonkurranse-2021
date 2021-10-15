import requests
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
from app import app


# convert snake case variables to readable text with capitalized letter
def convert_snake(snake_case):
    return snake_case.replace("_", " ").title()


def convert_slugs(snake_case):
    return snake_case.replace("-", " ").title()


def get_collection_slug():
    url = "https://api.opensea.io/api/v1/collections?offset=0&limit=300"
    response = requests.request("GET", url)
    data = response.json()
    df = pd.json_normalize(data['collections'])
    # only need a certain set of columns
    df = pd.DataFrame(df)
    collection = df['slug'].tolist()
    return collection


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
                    html.P(card_collection, className="card-text"),
                    html.P(card_price, className="card-text"),
                ],
                className="card-body",
            ),
        ],
        className="card border-primary col"
    )


def create_cardgrid(data):
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['name'][item], data['collection.name'][item],
                                 data['last_sale.total_price'][item], data['token_id'][item],
                                 data['asset_contract.address'][item]))
    return html.Div(cards, className="col_card_grid row row-cols-5")


def create_layout():
    collections = get_collection_slug()
    # sale_price param does not work on query - status 500 internal service error
    order_by_list = ['pk', 'sale_date', 'sale_count']

    controls = [
        html.Div(
            [
                dbc.Label("Collection", className="form-label"),
                dbc.Select(
                    id="collection-input",
                    className="form-select",
                    options=[{'label': 'Select all', 'value': ''}] +
                            [{"label": convert_slugs(c), "value": c}
                             for c in collections],
                    value='',  # set select all to default value
                ),
            ],
            className="form-group",
        ),
        html.Div(
            [
                dbc.Label("Sort by", className="form-label"),
                dbc.Select(
                    id="order-by-input",
                    className="form-select",
                    value=order_by_list[0],
                    options=[
                        {"label": convert_snake(o), "value": o}
                        for o in order_by_list
                    ],
                ),
            ],
            className="form-group",
        ),
        html.Div(
            [
                dbc.Label("Order", className="form-check-label"),
                dbc.RadioItems(
                    options=[
                        {"label": "desc", "value": "desc"},
                        {"label": "asc", "value": "asc"},
                    ],
                    value="desc",
                    id="order-direction-input",
                ),
            ],
            className="form-group",
        ),
        html.Div(
            [
                dbc.Label("Page"),
                html.Br(),
                dbc.Pagination(max_value=5, first_last=True, active_page=1, id="asset_pagination",
                               className="pagination"),
            ]
        ),
    ]

    return html.Div(
        children=[
            html.Div(
                [
                    dbc.Card([dbc.CardHeader("Filter", className="card-header"),
                              dbc.CardBody([dbc.Row([dbc.Col(c) for c in controls])], className="card-body")],
                             body=True,
                             className="card border-light mb-3"),  # create sorting controls

                ],
                className="header",
            ),
            html.Div(id="card-grid-content"),
        ],
        className="main"
    )


@app.callback(
    Output("card-grid-content", "children"),
    [Input("collection-input", "value"),
     Input("order-by-input", "value"),
     Input("order-direction-input", "value"),
     Input("asset_pagination", "active_page")]
)
def update_grid(collection, order_by, order_direction, page_no):
    limit = 20
    page_no = page_no
    offset = (page_no * limit) - limit
    # collection = ""
    assets = get_assets(order_by, order_direction, offset, limit, collection)
    return create_cardgrid(assets)
