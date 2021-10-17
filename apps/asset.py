import requests
import pandas as pd
import dash
import json
import dash_bootstrap_components as dbc
from urllib.parse import urlparse, parse_qsl, urlencode
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
from app import app


def get_single_asset(asset_contract_address, token_id):
    url = "https://api.opensea.io/api/v1/asset/{asset_contract_address}/{token_id}/".format(
        asset_contract_address=asset_contract_address, token_id=token_id)
    response = requests.request("GET", url)
    data = response.json()
    df = pd.json_normalize(data)
    df = pd.DataFrame(df)
    df_orders = pd.json_normalize(data['orders'])
    # convert values to float/int to calculate prices later
    df_orders['current_price'] = df_orders['current_price'].astype(float)
    df_orders['payment_token_contract.usd_price'] = df_orders['payment_token_contract.usd_price'].astype(float)
    df_orders['quantity'] = df_orders['quantity'].astype(int)
    pd.set_option('display.max_colwidth', None)  # extend colwidth to display whole value, instead of partial values
    return df, df_orders


def get_more_from_collection(collection):
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"limit": "3", "collection": f"{collection}"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    col_list = ['id', 'token_id', 'name', 'image_url', 'asset_contract.address']
    df = pd.DataFrame(df, columns=col_list)
    return df


def create_card(card_img, card_title, token_id, asset_contract_address):
    asset_link = dbc.CardLink("{name}".format(name=card_title),
                              href="/asset?asset_contract_address={address}&token_id={token_id}".format(
                                  address=asset_contract_address, token_id=token_id))
    return dbc.Card(
        [
            dbc.CardImg(src=card_img, top=True),
            dbc.CardBody(
                html.H4(asset_link, className="card-title"),
                className="card-body",
            ),
        ],
        className="card border-primary col"
    )


def gen_traits(asset):
    # print(asset.columns)
    trait_cards = []
    for trait in asset['traits']:
        # print(trait)
        card = dbc.Card(
            dbc.CardBody(
                [
                    # html.H4(asset['traits.value'][trait], className="card-title"),
                    # html.H6(asset['traits.trait_type'][trait], className="card-subtitle"),
                    html.P(
                        "Some quick example text",
                        className="card-text",
                    ),
                ],
                className="card-body",
            ),
            # style={"width": "18rem"},
            className="card border-info col",
        )
        trait_cards.append(card)
        # asset['traits.trait_count'][trait] #round up/down
    return html.Div(trait_cards, className="col_card_grid row row-cols-4")


def create_layout(url_query):
    # get asset corresponding to the ones the user clicked on earlier
    asset_contract_address = url_query['asset_contract_address']
    token_id = url_query['token_id']
    dcc.Location(id='url', refresh=False),
    asset, asset_orders = get_single_asset(asset_contract_address, token_id)

    current_price = (asset_orders['current_price'][0] / pow(10, asset_orders['payment_token_contract.decimals'][0]))
    current_price_usd = (((asset_orders['current_price'][0] / pow(10,
                                                                  asset_orders['payment_token_contract.decimals'][0])) *
                          asset_orders['payment_token_contract.usd_price'][0]) / asset_orders['quantity'][0])
    fav_btn_heart = html.Button(id='fav_btn_hrt', className="fav-btn-hrt",
                                children=[html.Img(
                                    src='data:image/svg+xml;base64,'
                                        'PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0xMiAyMS41OTNjLTUuNjMtNS41MzktMTEtMTAuMjk3LTExLTE0LjQwMiAwLTMuNzkxIDMuMDY4LTUuMTkxIDUuMjgxLTUuMTkxIDEuMzEyIDAgNC4xNTEuNTAxIDUuNzE5IDQuNDU3IDEuNTktMy45NjggNC40NjQtNC40NDcgNS43MjYtNC40NDcgMi41NCAwIDUuMjc0IDEuNjIxIDUuMjc0IDUuMTgxIDAgNC4wNjktNS4xMzYgOC42MjUtMTEgMTQuNDAybTUuNzI2LTIwLjU4M2MtMi4yMDMgMC00LjQ0NiAxLjA0Mi01LjcyNiAzLjIzOC0xLjI4NS0yLjIwNi0zLjUyMi0zLjI0OC01LjcxOS0zLjI0OC0zLjE4MyAwLTYuMjgxIDIuMTg3LTYuMjgxIDYuMTkxIDAgNC42NjEgNS41NzEgOS40MjkgMTIgMTUuODA5IDYuNDMtNi4zOCAxMi0xMS4xNDggMTItMTUuODA5IDAtNC4wMTEtMy4wOTUtNi4xODEtNi4yNzQtNi4xODEiLz48L3N2Zz4=')]),
    fav_btn = dbc.Button('Save', id='fav_btn', className="fav-btn", color='dark')

    def create_cardgrid():
        data = get_more_from_collection(asset['collection.slug'].to_string(index=False))
        cards = []
        for item in data.index:
            cards.append(create_card(data['image_url'][item], data['name'][item],
                                     data['token_id'][item],
                                     data['asset_contract.address'][item]))
        return html.Div(cards, className="col_card_grid row row-cols-3")

    bid_window = dbc.Modal(
        [
            dbc.ModalHeader("Bid"),
            dbc.ModalBody("Put in your bid. Decimals are indicated with ."),
            dbc.InputGroup(
                [
                    dbc.Input(id="bid_amount", placeholder="Amount", type="number"),
                    dbc.InputGroupText("ETH"),
                ],
            ),
            html.P(id="output_msg_bid"),
            dbc.ModalFooter([
                dbc.Button(
                    "Confirm", id="confirm_bid", className="ml-auto", n_clicks=0, color="dark"
                ),
                dbc.Button(
                    "Close", id="close_modal", className="ml-auto", n_clicks=0,
                )
            ],
            ),
        ],
        id="modal",
        is_open=False,
    )

    list_group = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                [
                    html.H5(asset['name']),
                    html.Small(asset['token_id']),
                ],

            ),
            dbc.ListGroupItem(
                [
                    html.H5('Current price'),
                    html.Div([
                        html.Img(src='{url}'.format(url=asset_orders['payment_token_contract.image_url'][0]),
                                 id="price_symbol"),
                        html.Small(current_price),
                        html.Small(f'(${current_price_usd})'),
                        dbc.Tooltip(asset_orders['payment_token_contract.symbol'][0],
                                    target="price_symbol",
                                    ),
                    ]),
                ],

            ),
            dbc.ListGroupItem(
                [
                    html.H5('Save', id="tooltip-favourites"),
                    html.Div(fav_btn),
                    html.P(id="output_fav"),
                ],

            ),
            dbc.Tooltip(
                "You can find a list of your saved assets on your profile",
                target="tooltip-favourites",
            ),
        ],
        horizontal="lg",
    )

    card = dbc.Card(
        dbc.CardBody(
            [
                list_group,
                dbc.Button("Place a bid", id="open", n_clicks=0, className="btn btn-primary"),
            ]
        ),
        # style={"width": "18rem"},
        className="border-light",
    )

    row1 = html.Tr([html.Td("Contract Address"), html.Td(asset['asset_contract.address'])])
    row2 = html.Tr([html.Td("Token ID"), html.Td(asset['token_id'])])
    row3 = html.Tr([html.Td("Token Standard"), html.Td("")])
    row4 = html.Tr([html.Td("Blockchain"), html.Td("")])

    table_body = [html.Tbody([row1, row2, row3, row4])]

    asset_details = html.Div(
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        html.P('Created by ' + asset['creator.user.username'], className="text-muted"),
                        html.P(asset['description']),
                    ],
                    title="Description", className="accordion-item",
                ),
                dbc.AccordionItem(
                    [
                        html.Img(src="{url}".format(url=asset['collection.image_url'].to_string(index=False))),  # todo
                        html.P(asset['collection.description']),
                    ],
                    title="About " + asset['collection.name'], className="accordion-item",
                ),
                dbc.AccordionItem(
                    gen_traits(asset),
                    title="Traits", className="accordion-item",
                ),
                dbc.AccordionItem(
                    table_body,
                    title="Details", className="accordion-item",
                ),
            ],
            flush=True,
            className="accordion",
        )
    )

    asset_stats = html.Div(
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    html.P("text"),
                    title="Price history", className="accordion-item",
                ),
                dbc.AccordionItem(
                    html.P("text"),
                    title="Offers", className="accordion-item",
                ),
                dbc.AccordionItem(
                    html.P("text"),
                    title="Trading history", className="accordion-item",
                ),
                dbc.AccordionItem(
                    create_cardgrid(),
                    title="More from this collection", className="accordion-item",
                ),
            ],
            flush=True,
            className="accordion",
        )
    )

    return html.Div(
        children=[
            dcc.Store(id="address_token"),
            # HEADER
            html.Div(id='url_path'),
            html.Div(
                children=[
                    # html.H1('NFT', id='header-text'),
                ],
                className="header",
            ),
            # INFO
            html.Div(id="content"),

            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.Div(html.Div(html.Img(src='{img_url}'.format(img_url=asset['image_url'][0])),
                                                      className="NFT-src"))),
                            dbc.Col(html.Div(card)),
                        ]
                    ),
                ]
            ),
            dbc.Button("Open on opensea", id="opensea_link", n_clicks=0,
                       href='{url}'.format(url=asset['permalink'].to_string(index=False)), className="btn btn-primary"),
            bid_window,
            asset_details,
            asset_stats,
        ],
        className="main"
    )


# save contract address and token_id in local storage in browser
@app.callback(Output("address_token", "data"),
              [Input("url", "href")])
def display_page(path_href):
    # get query string from url as dictionary
    parse_result = urlparse(path_href)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    return state


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"),
     Input("close_modal", "n_clicks")],
    [State("modal", "is_open")]
)
def show_modal(n_bid, n_close, is_open):
    if n_bid or n_close:
        return not is_open
    return is_open


@app.callback(
    Output("output_msg_bid", "children"),
    [Input("confirm_bid", "n_clicks"),
     Input('address_token', 'data')],
    [State("bid_amount", "value")]
)
def accept_bid(n_confirm, asset, n_amount):
    if n_confirm:
        bid_asset = {
            "asset_contract_address": "{address}".format(address=asset['asset_contract_address']),
            "token_id": "{id}".format(id=asset['token_id']),
            "price": "{price}".format(price=n_amount)
        }
        write_json(bid_asset, 'bids', 'bids.json')
        return f"Bid of {n_amount} ETH accepted!"


@app.callback(
    Output("output_fav", "children"),
    [Input("fav_btn", "n_clicks"),
     Input('address_token', 'data')]
)
def add_favourite(n_fav, asset):
    if n_fav:
        fav_asset = {
            "asset_contract_address": "{address}".format(address=asset['asset_contract_address']),
            "token_id": "{id}".format(id=asset['token_id']),
        }
        write_json(fav_asset, 'favourites', 'favourites.json')
        return "wohoo"


def write_json(new_json, name, filename):
    with open(filename, 'r+') as file:
        # print(new_json)
        file_data = json.load(file)  # load data into dict
        # print(file_data)
        # if new_json not in file_data:
        file_data[name].append(new_json)
        file.seek(0)
        json.dump(file_data, file, indent=4)
        # TODO dont allow duplicates
