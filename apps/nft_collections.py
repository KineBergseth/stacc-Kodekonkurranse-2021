import requests
import pandas as pd
import dash
import json
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app


def get_collection(offset, slug):
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"order_direction": "desc", "offset": {offset}, "limit": "12", "collection": {slug}}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    col_list = ['id', 'token_id', 'image_url', 'name', 'asset_contract.address', 'collection.name']
    df = pd.DataFrame(df, columns=col_list)
    # print(df)
    return df


def create_card(card_img, card_collection, card_title, card_price, token_id, asset_contract_address):
    asset_link = dbc.CardLink("{name}".format(name=card_title), href="/asset?asset_contract_address={address}&token_id={token_id}".format(address=asset_contract_address, token_id=token_id))
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


def create_cardgrid(offset, slug):
    data = get_collection(offset, slug)
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['collection.name'][item], data['name'][item], 'price', data['token_id'][item], data['asset_contract.address'][item]))
    return html.Div(dbc.CardColumns(cards, className="col_card_grid"), className='col_box')


pagination = dbc.FormGroup(
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
)


def create_layout(app):
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H1('Collections', id='header-text'),
                    html.P('Utforsk noen utvalgte collections. Trykk på bildeknappene for å se utvalget',
                           id='introduction-text'),
                    html.Div([
                        html.Button(id='dotdotdots', className="col-btn",
                                    children=[html.Img(
                                        src='https://lh3.googleusercontent.com/lIo17HAEF8FwPEJZOD9xg'
                                            '-SLk9hAcDc0sjiviGY63KR1py7BGd78Xpv_SIPfhCINZq16pF'
                                            '-rlwfTuq68dvuL7uhCU_FPKLnT16oS=s120')]),
                        html.Button(id='bears-deluxe', className="col-btn",
                                    children=[html.Img(
                                        src='https://lh3.googleusercontent.com'
                                            '/InPgClcuGiNA5TdEGTu7zuGSv1LDJ54L_sC49G7fqJ0YawDcdmN78t7iShcrbyQ_sdoUyjyBAoXVMTKaaf9OP8ekDyBaEEWJMiDbi8M=s120')]),
                        html.Button(id='sappy-seals', className="col-btn",
                                    children=[html.Img(
                                        src='https://lh3.googleusercontent.com'
                                            '/c_wASW_EH06TmUJTAfZ9HYAx8rhKbu3SbOqpHHp0OistKOTJcPDjhSBg3S6OM3HG9ivBpVVtSnKkNJKilZQCc_8V1kTG7JQDSzmWoQ=s120')]),
                        html.Button(id='gutterpigeons', className="col-btn",
                                    children=[html.Img(
                                        src='https://lh3.googleusercontent.com/UoABiu1ydkR50jb_G2BPJO1I9dQ30o6DzRY2RCPoo'
                                            '-etNtb77FRj2WxoxG_sYL6C6I5qiu88g6BpAX6GfIGjuFPcZQ_beA_M8TWpQDM=s120')]),
                        html.Button(id='epiceagles', className="col-btn",
                                    children=[html.Img(
                                        src='https://lh3.googleusercontent.com/BMCuX'
                                            '-_CakY3bKgjl7mxVgAKKug2D1xdWNcenSeKYReZtIfYGD1Uo0BN7nIeDtRIsgu6Xz8b90AYGCqn8EvKWhaiHJ2-OVu0Oos-NA=s120')]),
                        html.Button(id='infinity-frogs-nft', className="col-btn",
                                    children=[html.Img(
                                        src='https://lh3.googleusercontent.com'
                                            '/5tHPLRm3oJiR0xNSIuBvZthmH2bOC81QC2AE6N6tnV1xBzqV8h2QQDJb6IErqEiUp4CEUlUOvcxjB3NDKAajCocluKd577H1u2LU3es=s120')])
                    ],
                        className="collection_buttons",
                    ),
                ],
                className="header",
            ),
            # pagination,
            html.Div(id="collection_content"),
            # dbc.Button("close", id="close", n_clicks=0, color="dark", outline=True, href="#collection_content"),
            # dcc.location

        ],
        className="main"
    )


@app.callback(
    Output("collection_content", "children"),
    [
        Input("dotdotdots", "n_clicks"),
        Input("bears-deluxe", "n_clicks"),
        Input("sappy-seals", "n_clicks"),
        Input("gutterpigeons", "n_clicks"),
        Input("epiceagles", "n_clicks"),
        Input("infinity-frogs-nft", "n_clicks"),
    ]
)
def generate_table(n_col1, n_col2, n_col3, n_col4, n_col5, n_col6):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    slug = button_id  # collection reference
    offset = 0
    return create_cardgrid(offset, slug)
