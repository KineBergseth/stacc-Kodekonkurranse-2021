import requests
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, Input, Output
from app import app


# convert snake case variables to readable text with capitalized letter
def convert_snake(snake_case):
    return snake_case.replace("_", " ").title()


def convert_slugs(snake_case):
    return snake_case.replace("-", " ").title()


def convert_price(price):
    """
    Convert currency value from WEI to ETH if its not nan
    :param price: amount in WEI
    :return: amount in ETH
    """
    if pd.isna(price):
        return price
    else:
        return f"{(price / pow(10, 18))} ETH"


def get_collection_slug():
    """
    Get a set of 300 slugs to display in the collections dropdownlist
    :return: list of 300 unique slugs
    """
    url = "https://api.opensea.io/api/v1/collections?offset=0&limit=300"
    response = requests.request("GET", url)
    data = response.json()
    df = pd.json_normalize(data['collections'])
    df = pd.DataFrame(df)
    collection = df['slug'].tolist()
    return collection


def get_assets(order_by, order_direction, offset, limit, collection):
    """
    Get assets to display on page
    :param order_by: how to order the assets
    :param order_direction: asc/desc direction
    :param offset: offset for request
    :param limit: how many assets are shown on the page
    :param collection: unique slug that gets assets belonging to that collection
    :return: dataframe containing data about all assets fetched
    """
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"order_by": f"{order_by}", "order_direction": f"{order_direction}", "offset": f"{offset}",
                   "limit": f"{limit}", "collection": f"{collection}"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    col_list = ['id', 'token_id', 'name', 'image_url', 'collection.name', 'last_sale.total_price',
                'asset_contract.address']
    df = pd.DataFrame(df, columns=col_list)
    # convert price from last sale to float, so i can do math
    df['last_sale.total_price'] = df['last_sale.total_price'].astype(float)
    df['last_sale.total_price'] = df['last_sale.total_price'].apply(convert_price)
    return df


def create_card(card_img, card_collection, card_title, card_price, token_id, asset_contract_address):
    """
    Create a card with data about a specific NFT
    :param card_img: image link
    :param card_collection: collection name
    :param card_title: name of NFT
    :param card_price: price from last sale in ETH
    :param token_id: token id for NFT
    :param asset_contract_address:  contract address for NFT
    :return: html with data for an asset
    """
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
        className="card border-secondary col"
    )


def create_cardgrid(data):
    """
    Create cardgrid with a card for each asset
    :param data: dataframe containing asset data
    :return: html grid containing all the individual cards
    """
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['name'][item], data['collection.name'][item],
                                 data['last_sale.total_price'][item], data['token_id'][item],
                                 data['asset_contract.address'][item]))
    return html.Div(cards, className="col_card_grid row row-cols-5")


def create_layout():
    collections = get_collection_slug()
    # sale_price param does not work on query - status 500 internal service error
    order_by_list = ['pk', 'sale_date', 'sale_count']  # order choices

    # create filter controls
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
        [
            html.Div(
                [
                    dbc.Card([dbc.CardHeader("Filter", className="card-header text-muted"),
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
    """
    Takes input and creates the grid based on choices or default values
    :param collection: collection name
    :param order_by: order of assets
    :param order_direction: asc/desc
    :param page_no: the current page number, for pagination/offset
    :return: card grid with data matching applied filter
    """
    limit = 20
    page_no = page_no
    offset = (page_no * limit) - limit
    assets = get_assets(order_by, order_direction, offset, limit, collection)
    return create_cardgrid(assets)
