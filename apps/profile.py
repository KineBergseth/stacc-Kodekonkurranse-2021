import requests
import pandas as pd
import dash
import json
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import random

from app import app


def create_layout(app):
    return html.Div([
        html.H1('User profile'),
        html.P('Here you can find stuff'),
        dcc.Tabs(id="profile-tabs", children=[
            dcc.Tab(label='Favorites', value='fav-tab'),
            dcc.Tab(label='Your active bids', value='bid-tab'),
            dcc.Tab(label='Your uploaded NFTs', value='upload-tab'),
        ]),
        html.Div(id='profile-content-tabs')
    ])


def add_imgmarkdown(url):
    return "<img src='{url}' height='75' />".format(url=url)


def generate_table(data):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    asset_data = data
    return dash_table.DataTable(
        id='table',
        data=asset_data.to_dict('records'),
        columns=[
            {"id": "image_url", "name": "NFT", "presentation": "markdown"},
            {"id": "name", "name": "name"},
            {"id": "price", "name": "Current price/bid"},
        ],
        markdown_options={"html": True},
        sort_action='native',
        style_cell={'textAlign': 'left', "whiteSpace": "pre-line"},
        style_as_list_view=True,
    )


def get_asset(asset_contract_address, token_id):
    url = "https://api.opensea.io/api/v1/asset/{asset_contract_address}/{token_id}/".format(
        asset_contract_address=asset_contract_address, token_id=token_id)
    response = requests.request("GET", url)
    return response.json()


def get_NFTs(df):
    bids = []
    for item in df.index:
        bids.append(get_asset(df['asset_contract_address'][item], df['token_id'][item]))
    df = pd.json_normalize(bids)
    col_list = ['id', 'token_id', 'asset_contract.address', 'image_url', 'name']
    df = pd.DataFrame(df, columns=col_list)
    df['image_url'] = df['image_url'].apply(add_imgmarkdown)
    df = df.rename(columns={'asset_contract.address': 'asset_contract_address'})
    return df


def random_bid_gen():
    random_bid = random.randint(0, 40)
    return random_bid


def tab_favs():
    f = open('favourites.json', )
    fav_data = json.load(f)
    df_fav = pd.DataFrame(fav_data['favourites'])
    df = get_NFTs(df_fav)
    return generate_table(df)


def tab_bids():
    f = open('bids.json', )
    bid_data = json.load(f)
    df_bid = pd.DataFrame(bid_data['bids'])
    df = get_NFTs(df_bid)
    result = pd.merge(df, df_bid)
    return generate_table(result)


# \n for linjeskift "your bid is \n X ETH
def tab_uploads():
    f = open('uploads.json', )
    uploaded_data = json.load(f)
    df_uploads = pd.DataFrame(uploaded_data['uploaded_nfts'])
    col_list = ['id', 'token_id', 'asset_contract.address', 'image_url', 'name']
    df = pd.DataFrame(df_uploads, columns=col_list)
    df['image_url'] = df['image_url'].apply(add_imgmarkdown)

    # generate some random fictive bids for the users uploaded NFTs
    fictive_bids = []
    for row in df.index:
        fictive_bids.append(random_bid_gen())
    df['price'] = fictive_bids
    return generate_table(df)


@app.callback(Output('profile-content-tabs', 'children'),
              Input('profile-tabs', 'value'))
def render_tabcontent(tab):
    if tab == 'fav-tab':
        return tab_favs()
    elif tab == 'bid-tab':
        return tab_bids()
    elif tab == 'upload-tab':
        return tab_uploads()
