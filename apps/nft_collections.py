import requests
import pandas as pd
import dash
import json
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app


def get_collection(offset, limit, slug):
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"offset": f"{offset}", "limit": f"{limit}", "collection": f"{slug}"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    col_list = ['id', 'token_id', 'image_url', 'name', 'asset_contract.address', 'collection.name']
    df = pd.DataFrame(df, columns=col_list)
    return df


def create_card(card_img, card_collection, card_title, token_id, asset_contract_address):
    asset_link = dbc.CardLink("{name}".format(name=card_title),
                              href="/asset?asset_contract_address={address}&token_id={token_id}".format(
                                  address=asset_contract_address, token_id=token_id))
    return dbc.Card(
        [
            dbc.CardImg(src=card_img, top=True),
            dbc.CardBody(
                [
                    html.H4(asset_link, className="card-title"),
                    # html.P(card_collection, className="card-collection"),
                ],
                className="asset_cardbody",
            ),
        ],
        color="dark",
        inverse=True,
        className="asset_card col"
    )


def create_cardgrid(offset, limit, slug):
    data = get_collection(offset, limit, slug)
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['collection.name'][item], data['name'][item],
                                 data['token_id'][item], data['asset_contract.address'][item]))
    return html.Div([html.H1(data['collection.name'][0]), html.Div(cards, className="col_card_grid row row-cols-4")],
                    className='col_box')


def create_layout(app):
    return html.Div(
        children=[
            dcc.Store(id='col_slug'),
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
            html.Div(id="col_pag"),
            html.Div(id="collection_content"),
        ],
        className="main"
    )


@app.callback(
    Output("col_slug", "data"),
    Output("col_pag", "children"),
    [
        Input("dotdotdots", "n_clicks"),
        Input("bears-deluxe", "n_clicks"),
        Input("sappy-seals", "n_clicks"),
        Input("gutterpigeons", "n_clicks"),
        Input("epiceagles", "n_clicks"),
        Input("infinity-frogs-nft", "n_clicks")
    ]
)
def generate_table(n_col1, n_col2, n_col3, n_col4, n_col5, n_col6):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    slug = button_id  # collection reference

    return slug, dbc.Pagination(max_value=5, first_last=True, active_page=1, id="collection_pagination")
    #return create_cardgrid(offset, limit, slug)


@app.callback(Output("collection_content", "children"),
              [Input("col_slug", "data"), Input("collection_pagination", "active_page")])
def pagination(slug, page_no):
    limit = 12
    page_no = page_no
    offset = (page_no * limit) - limit
    return create_cardgrid(offset, limit, slug)
