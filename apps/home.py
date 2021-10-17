import dash_bootstrap_components as dbc
import requests
import pandas as pd
from dash import html


def get_new_auction():
    """
    Get 5 newly created auctions to display in carousel
    :return: dataframe with data about NFTs
    """
    url = "https://api.opensea.io/api/v1/events"
    querystring = {"event_type": "created", "only_opensea": "true", "offset": "0", "limit": "5"}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['asset_events'])
    col_list = ['asset.token_id', 'asset.image_url', 'asset.name', 'asset.contract_address']
    df = pd.DataFrame(df, columns=col_list)
    return df


def create_slides(data):
    """
    Create slides for carousel and populate them with data from NFTs
    :param data: dataframe containing NFT data
    :return: list of slides for carousel
    """
    slides = []
    for item in data.index:
        slides.append({
            "key": item,
            "src": data['asset.image_url'][item],
            "header": data['asset.name'][item],
        })
    return slides


def create_layout():
    """
    Creates the layout for the home page
    :return: layout with all the elements in
    """
    carousel = dbc.Carousel(
        items=create_slides(get_new_auction()),
        className="carousel"
    )

    cards = dbc.CardGroup(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Explore", className="card-title text-center"),
                        html.P(
                            "Browse thousands of NFTs on our marketplace, and discover different collections",
                            className="card-text",
                        ),
                        dbc.CardLink("marketplace", href="/marketplace", className="card-link"),
                        dbc.CardLink("collections", href="/collections", className="card-link"),
                    ]
                )
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Sell your NFTs", className="card-title text-center"),
                        html.P(
                            "Upload your own NFTs, add metadata and list them for sale",
                            className="card-text",
                        ),
                        dbc.CardLink("upload here", href="/upload", className="card-link"),
                    ]
                )
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Profile", className="card-title text-center"),
                        html.P('''On your own profile you can keep track on NFTs your have added to your favourites, 
                            keep track of the NFTs you have placed bids on and view your uploaded assets ''',
                               className="card-text",
                               ),
                        dbc.CardLink("go to profile", href="/profile", className="card-link"),
                    ]
                )
            ),
        ],
        className="mt-5",
    )

    return html.Div(
        [
            html.Div(
                [
                    html.H1('New auctions', className='header-text text-center mt-3'),
                ],
                className="header",
            ),
            carousel,
            cards,
        ],
        className="main"
    )
