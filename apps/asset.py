import requests
import pandas as pd
import dash
import json
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app

asset_contract_address = '0xa2480eb41dd1f2b0abade9f305826c544d47f696'
token_id = '6771'


def get_single_asset(asset_contract_address, token_id):
    url = "https://api.opensea.io/api/v1/asset/{asset_contract_address}/{token_id}/".format(
        asset_contract_address=asset_contract_address, token_id=token_id)
    response = requests.request("GET", url)
    data = response.json()

    df = pd.json_normalize(data)
    # col_list = ['id', 'token_id', 'asset_contract.address', 'image_url', 'name']
    df = pd.DataFrame(df)  # , columns=col_list)
    return df


# get_single_asset('0xf43aaa80a8f9de69bc71aea989afceb8db7b690f', '7799')
asset = get_single_asset(asset_contract_address, token_id)

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
    style={"width": "18rem"},
    className="border-light",
)


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
    # we use this function to make the example items to avoid code duplication
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


bid_window = dbc.Modal(
    [
        dbc.ModalHeader("Bid"),
        dbc.ModalBody("put in bid here"),
        dbc.InputGroup(
            [
                dbc.Input(placeholder="Amount", type="number"),
                dbc.InputGroupAddon(".00", addon_type="append"),
            ],
        ),
        dbc.Input(id="input", placeholder="place big in ETH", type="number"),
        dbc.ModalFooter(
            dbc.Button(
                "Confirm", id="close", className="ml-auto", n_clicks=0
            )
        ),
    ],
    id="modal",
    is_open=False,
)


def create_layout(app):
    return html.Div(
        children=[
            # HEADER
            html.Div(
                children=[
                    # html.H1('NFT', id='header-text'),
                ],
                className="header",
            ),
            # INFO
            html.Div(id="content"),
            html.Div(html.Img(src='{img_url}'.format(img_url=asset['image_url'])),
                     className="NFT-src"),
            card,
            bid_window,

            html.Div(
                [accordion_desc(1), make_item(2), make_item(3), accordion_details(4)], className="accordion"
            ),

        ],
        className="main"
    )


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
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(Output("output", "children"), [Input("input", "value")])
def output_text(value):
    return value
