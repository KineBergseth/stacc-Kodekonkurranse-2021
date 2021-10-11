import requests
import pandas as pd
import dash
import json
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State
from urllib.parse import urlparse, parse_qsl, urlencode

from app import app


def get_single_asset(asset_contract_address, token_id):
    url = "https://api.opensea.io/api/v1/asset/{asset_contract_address}/{token_id}/".format(
        asset_contract_address=asset_contract_address, token_id=token_id)
    response = requests.request("GET", url)
    data = response.json()

    df = pd.json_normalize(data)
    # col_list = ['id', 'token_id', 'asset_contract.address', 'image_url', 'name']
    df = pd.DataFrame(df)  # , columns=col_list)
    return df


def accordion_desc(i):
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Description",
                        color="link",
                        id=f"group-{i}-toggle",
                        n_clicks=0,
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody(f"Created by, description"),
                id=f"collapse-{i}",
                is_open=False,
            ),
        ]
    )


def accordion_details(i):
    table_header = [
        html.Thead(html.Tr([html.Th("Key"), html.Th("Value")]))
    ]

    row1 = html.Tr([html.Td("Contract Address"), html.Td("")])
    row2 = html.Tr([html.Td("Token ID"), html.Td("")])
    row3 = html.Tr([html.Td("Token Standard"), html.Td("")])
    row4 = html.Tr([html.Td("Blockchain"), html.Td("")])

    table_body = [html.Tbody([row1, row2, row3, row4])]
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Details",
                        color="link",
                        id=f"group-{i}-toggle",
                        n_clicks=0,
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody(dbc.Table(table_body, bordered=True)),
                id=f"collapse-{i}",
                is_open=False,
            ),
        ]
    )


def make_item(i):
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Collapsible group #{i}",
                        color="link",
                        id=f"group-{i}-toggle",
                        n_clicks=0,
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody(f"This is the content of group {i}..."),
                id=f"collapse-{i}",
                is_open=False,
            ),
        ]
    )


fav_btn_heart = html.Button(id='fav_btn_hrt', className="fav-btn-hrt",
                      children=[html.Img(
                          src='data:image/svg+xml;base64,'
                              'PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0xMiAyMS41OTNjLTUuNjMtNS41MzktMTEtMTAuMjk3LTExLTE0LjQwMiAwLTMuNzkxIDMuMDY4LTUuMTkxIDUuMjgxLTUuMTkxIDEuMzEyIDAgNC4xNTEuNTAxIDUuNzE5IDQuNDU3IDEuNTktMy45NjggNC40NjQtNC40NDcgNS43MjYtNC40NDcgMi41NCAwIDUuMjc0IDEuNjIxIDUuMjc0IDUuMTgxIDAgNC4wNjktNS4xMzYgOC42MjUtMTEgMTQuNDAybTUuNzI2LTIwLjU4M2MtMi4yMDMgMC00LjQ0NiAxLjA0Mi01LjcyNiAzLjIzOC0xLjI4NS0yLjIwNi0zLjUyMi0zLjI0OC01LjcxOS0zLjI0OC0zLjE4MyAwLTYuMjgxIDIuMTg3LTYuMjgxIDYuMTkxIDAgNC42NjEgNS41NzEgOS40MjkgMTIgMTUuODA5IDYuNDMtNi4zOCAxMi0xMS4xNDggMTItMTUuODA5IDAtNC4wMTEtMy4wOTUtNi4xODEtNi4yNzQtNi4xODEiLz48L3N2Zz4=')]),
fav_btn = dbc.Button('Save', id='fav_btn', className="fav-btn", color='dark')

bid_window = dbc.Modal(
    [
        dbc.ModalHeader("Bid"),
        dbc.ModalBody("Put in your bid. Decimals are indicated with ."),
        dbc.InputGroup(
            [
                dbc.Input(id="bid_amount", placeholder="Amount", type="number"),
                dbc.InputGroupAddon("ETH", addon_type="append"),
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


def create_layout(url_query):
    # get asset corresponding to the ones the user clicked on earlier
    asset_contract_address = url_query['asset_contract_address']
    token_id = url_query['token_id']
    dcc.Location(id='url', refresh=False),
    asset = get_single_asset(asset_contract_address, token_id)
    # print(asset.columns)

    list_group = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                [
                    dbc.ListGroupItemHeading(asset['name']),
                    dbc.ListGroupItemText(asset['token_id']),
                ],

            ),
            dbc.ListGroupItem(
                [
                    dbc.ListGroupItemHeading('price'),
                    dbc.ListGroupItemText('0.003 ETH'),
                ],

            ),
            dbc.ListGroupItem(
                [
                    dbc.ListGroupItemHeading('Save', id="tooltip-favourites"),
                    dbc.ListGroupItemText(fav_btn),
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
                dbc.Button("Place a bid", id="open", n_clicks=0, color="dark"),
            ]
        ),
        # style={"width": "18rem"},
        className="border-light",
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

            bid_window,

            html.Div(
                [accordion_desc(1), make_item(2), make_item(3), accordion_details(4)], className="accordion"
            ),

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
    [Output(f"collapse-{i}", "is_open") for i in range(1, 5)],
    [Input(f"group-{i}-toggle", "n_clicks") for i in range(1, 5)],
    [State(f"collapse-{i}", "is_open") for i in range(1, 5)],
)
def toggle_accordion(n1, n2, n3, n4, is_open1, is_open2, is_open3, is_open4):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-1-toggle" and n1:
        return not is_open1, False, False, False
    elif button_id == "group-2-toggle" and n2:
        return False, not is_open2, False, False
    elif button_id == "group-3-toggle" and n3:
        return False, False, not is_open3, False
    elif button_id == "group-4-toggle" and n4:
        return False, False, False, not is_open4
    return False, False, False, False


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
    bid_asset = {
        "asset_contract_address": "{address}".format(address=asset['asset_contract_address']),
        "token_id": "{id}".format(id=asset['token_id']),
        "price": "{price}".format(price=n_amount)
    }

    if n_confirm:
        write_json(bid_asset)
        return f"Bid of {n_amount} ETH accepted!"


def write_json(new_bid, filename='bids.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)  # load data into dict
        file_data['bids'].append(new_bid)
        file.seek(0)
        json.dump(file_data, file, indent=4)
