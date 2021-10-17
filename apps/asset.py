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
    if asset["traits"].to_string(index=False) == '[]':  # maybe not the prettiest way to check if traits exists
        return html.P("This NFT has no traits")
    else:
        asset_traits = pd.json_normalize(asset['traits']).unstack().apply(pd.Series)
        asset_traits['trait_count'] = round(asset_traits['trait_count'].astype(float)/100)
        trait_cards = []
        for trait in asset_traits.index:
            percent = asset_traits['trait_count'][trait]
            card = dbc.Card(
                dbc.CardBody(
                    [
                        html.H6(asset_traits['trait_type'][trait], className="card-subtitle text-info text-center"),
                        html.H4(asset_traits['value'][trait], className="card-title text-center"),
                        html.P(
                            f"{percent}% have this trait",
                            className="card-text text-muted text-center",
                        ),
                    ],
                    className="card-body",
                ),
                className="card border-info col",
            )
            trait_cards.append(card)
        return html.Div(trait_cards, className="col_card_grid row row-cols-3")


def calculate_price(asset_orders):
    if 'current_price' in asset_orders.columns:
        current_price = (
                    asset_orders['current_price'][0] / pow(10, asset_orders['payment_token_contract.decimals'][0]))
        current_price_usd = (((asset_orders['current_price'][0] / pow(10, asset_orders[
            'payment_token_contract.decimals'][0])) * asset_orders['payment_token_contract.usd_price'][0]) /
                             asset_orders['quantity'][0])
        return dbc.ListGroupItem(
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
        )
    else:
        return dbc.ListGroupItem(
            [
                html.H5('Current price'),
                html.Div([
                    html.Small("No bids yet"),
                ]),
            ],
        )


def create_layout(url_query):
    # get asset corresponding to the ones the user clicked on earlier
    asset_contract_address = url_query['asset_contract_address']
    token_id = url_query['token_id']
    dcc.Location(id='url', refresh=False),
    asset, asset_orders = get_single_asset(asset_contract_address, token_id)
    if 'current_price' in asset_orders.columns:
        # if current bids exists, convert values to float/int to calculate prices
        asset_orders['current_price'] = asset_orders['current_price'].astype(float)
        asset_orders['payment_token_contract.usd_price'] = asset_orders['payment_token_contract.usd_price'].astype(
            float)
        asset_orders['quantity'] = asset_orders['quantity'].astype(int)

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
            dbc.ModalBody([html.P("Put in your bid. Decimals are indicated with ."),
                           html.P(f"You must bid higher than current price")]),
            dbc.InputGroup(
                [
                    dbc.Input(id="bid_amount", placeholder="Amount", type="number"),
                    dbc.InputGroupText("ETH"),
                ],
            ),
            html.P(id="output_msg_bid"),
            dbc.ModalFooter([
                dbc.Button(
                    "Confirm", id="confirm_bid", className="ml-auto btn btn-success", n_clicks=0
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

    asset_info = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                    html.H5(asset['name']),

            ),
            dbc.ListGroupItem(
                html.H5("Expiration date"),
            ),
            calculate_price(asset_orders),
            dbc.ListGroupItem(
                [
                    dbc.Button("Place a bid", id="open", n_clicks=0, className="btn btn-primary"),
                    dbc.Button('Save', id='fav_btn', className="btn btn-primary"),
                    html.P(id="output_fav"),
                ],

            ),
            dbc.Tooltip(
                "You can find a list of your saved assets on your profile",
                target="fav_btn",
            ),
        ],
    )

    address_link = html.A("{name}".format(name=asset['asset_contract.address'].to_string(index=False)), href='https://etherscan.io/address/{address}'.format(address=asset['asset_contract.address'].to_string(index=False)))
    row1 = html.Tr([html.Td("Contract Address"), address_link])
    row2 = html.Tr([html.Td("Token ID"), html.Td(asset['token_id'])])
    row3 = html.Tr([html.Td("Token Standard"), html.Td(asset['asset_contract.schema_name'])])

    table_body = [html.Tbody([row1, row2, row3])]

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
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Card(
                                [
                                    dbc.CardImg(src='{img_url}'.format(img_url=asset['image_url'][0]), top=True),
                                    dbc.CardBody(
                                            dbc.Button("Open on opensea", id="opensea_link", n_clicks=0,
                                                       href='{url}'.format(
                                                           url=asset['permalink'].to_string(index=False)),
                                                       className="btn btn-primary")
                                    ),
                                ],
                                style={"width": "18rem"},
                                className="card border-light",
                            ),
                            dbc.Col(asset_info),
                        ]
                    ),
                ]
            ),

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
        add = write_json(bid_asset, 'bids', 'bids.json')
        if add:
            return f"Bid of {n_amount} ETH accepted!"
        else:
            return "Cannot accept a new bid directly after your own"


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


def write_json(new_json, name, filename):
    with open(filename, 'r+') as file:
        file_data = json.load(file)  # load data into dict
        add = True
        for x in file_data[name]:
            if (new_json['asset_contract_address'] == x['asset_contract_address'] and new_json['token_id'] == x['token_id']):
        #if not any([new_json['asset_contract_address'] == x['asset_contract_address']):
                add = False
        if add:
            file_data[name].append(new_json)
            file.seek(0)
            json.dump(file_data, file, indent=4)
            print('yay')
            return True
        else:
            print('error error error')
            return False
