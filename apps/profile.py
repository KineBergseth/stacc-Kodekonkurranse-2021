import requests
import pandas as pd
import json
from dash import html, dcc, Input, Output
from dash.dash_table.Format import Format, Symbol
from dash import dash_table
import random
from app import app


def create_layout():
    """
    Create html display with all components
    :return: html with components
    """
    return html.Div(
        children=[
            html.H1('lizardlover23 profile', className="mt-3"),
            html.P('Welcome back @lizardlover23', className="text-muted"),
            html.P(['Here you can find an overview of your activity, such as your favorites assets, the bids you have '
                    'placed, and the NFTs you have upload and put for sale.', html.Br(),
                    'The display table has a built-in '
                    'sorting system']),
            dcc.Tabs(id="profile-tabs", children=[
                dcc.Tab(label='Favorites', value='fav-tab'),
                dcc.Tab(label='Your active bids', value='bid-tab'),
                dcc.Tab(label='Your uploaded NFTs', value='upload-tab'),
            ],
                     className="nav nav-tabs",
                     ),
            html.Div(id='profile-content-tabs')
        ])


def add_imgmarkdown(url):
    """
    Add html to link to display image
    :param url: NFT image link
    :return: link in html element
    """
    return "<img src='{url}' height='75' />".format(url=url)


def generate_table(data):
    """
    Generate datatable with data about NFTs added to collection
    :param data: dataframe with NFT data
    :return: HTML to render table
    """
    return dash_table.DataTable(
        id='table',
        data=data.to_dict('records'),
        columns=[
            {"id": "image_url", "name": "NFT", "presentation": "markdown"},
            {"id": "name", "name": "name"},
            {"id": "price", "name": "Current bid", 'format': Format().symbol(Symbol.yes).symbol_suffix('*'),
             },
        ],
        markdown_options={"html": True},
        sort_action='native',
        style_header={},
        style_cell={'textAlign': 'left', "whiteSpace": "pre-line"},
        style_as_list_view=True,
        editable=False,
        row_deletable=True,
    )


def get_asset(asset_contract_address, token_id):
    """
    Get a perticular NFT
    :param asset_contract_address:
    :param token_id:
    :return: json data about NFT
    """
    url = "https://api.opensea.io/api/v1/asset/{asset_contract_address}/{token_id}/".format(
        asset_contract_address=asset_contract_address, token_id=token_id)
    response = requests.request("GET", url)
    return response.json()


def get_NFTs(df):
    """
    For all NFTs in a dataframe, get more data from api
    :param df: dataframe with local stored data
    :return: dataframe with asset data
    """
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
    """
    Generate random number to add as fake bid on the users uploaded NFTS
    :return: int between 0-40
    """
    random_bid = random.randint(0, 40)
    return random_bid


def tab_favs():
    """
    Get favourite data from json and convert to df and create table
    :return: dataframe with NFT data
    """
    f = open('favourites.json', )
    fav_data = json.load(f)
    df_fav = pd.DataFrame(fav_data['favourites'])
    df = get_NFTs(df_fav)
    return generate_table(df)


def tab_bids():
    """
    Get bid data from json and convert to df and create table
    :return: dataframe with NFT data
    """
    f = open('bids.json', )
    bid_data = json.load(f)
    df_bid = pd.DataFrame(bid_data['bids'])
    df = get_NFTs(df_bid)
    result = pd.merge(df, df_bid)
    return generate_table(result)


def tab_uploads():
    """
    Get data about uploaded NFTs from json and convert to df and create table
    :return: dataframe with NFT data
    """
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
    """
    Render tab content based on user click input
    :param tab: tab id
    :return: call function to get correct data and generate datatable
    """
    if tab == 'fav-tab':
        return tab_favs()
    elif tab == 'bid-tab':
        return tab_bids()
    elif tab == 'upload-tab':
        return tab_uploads()
