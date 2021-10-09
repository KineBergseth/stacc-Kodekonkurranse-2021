import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
from app import app


# get 5 newly created auctions for carousel
def get_new_auction():
    url = "https://api.opensea.io/api/v1/events"
    querystring = {"event_type": "created", "only_opensea": "true", "offset": "0", "limit": "5"}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['asset_events'])
    col_list = ['asset.token_id', 'asset.image_url', 'asset.name', 'asset.contract_address']
    df = pd.DataFrame(df, columns=col_list)
    df = df.rename(columns={'asset.token_id': 'token_id', 'asset.image_url': 'image_url', 'asset.name': 'name',
                            'asset.contract_address': 'contract_address'})
    return df


def create_slides():
    data = get_new_auction()
    slides = []
    for item in data.index:
        slides.append({
            "key": item,
            "src": data['image_url'][item],
            "header": data['name'][item],
        })
    return slides


get_new_auction()
carousel = dbc.Carousel(
    items=create_slides(),
    className="carousel"
)

cards = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Explore", className="card-title glow"),
                    html.P(
                        "Browse thousands of NFTs on our marketplace, and put in bids"
                        "Discover collections",
                        className="card-text",
                    ),
                    dbc.CardLink("marketplace", href="/marketplace"),
                    dbc.CardLink("collections", href="/collections"),
                ]
            ),
            color="dark",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Sell your NFTs", className="card-title glow"),
                    html.P(
                        "Upload your own NFTs, add metadata and list them for sale",
                        className="card-text",
                    ),
                    dbc.CardLink("upload here", href="/asset?value=2457"),
                ]
            ),
            color="dark",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Profile", className="card-title glow"),
                    html.P('''On your own profile you can keep track on NFTs your have added to your favourites, 
                        keep track of the NFTs you have placed bids on and view your uploaded assets ''',
                           className="card-text",
                           ),
                    dbc.CardLink("go to profile", href="/profile"),
                ]
            ),
            color="dark",
        ),
    ]
)


def create_layout(app):
    return html.Div(
        children=[
            # HEADER
            html.Div(
                children=[
                    html.H1('NFT', id='header-text'),
                ],
                className="header",
            ),
            # INFO
            html.Div(id="content"),
            carousel,
            cards,
        ],
        className="main"
    )
