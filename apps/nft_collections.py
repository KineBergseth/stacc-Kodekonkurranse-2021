import requests
import pandas as pd
import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from app import app


def generate_img_buttons():
    """
    Generate image buttons for each collection
    :return: list of image buttons
    """
    # selected collections to display
    slugs = ['dotdotdots', 'bears-deluxe', 'sappy-seals', 'gutterpigeons', 'epiceagles', 'infinity-frogs-nft']
    image_links = ['https://lh3.googleusercontent.com/lIo17HAEF8FwPEJZOD9xg'
                   '-SLk9hAcDc0sjiviGY63KR1py7BGd78Xpv_SIPfhCINZq16pF-rlwfTuq68dvuL7uhCU_FPKLnT16oS=s120',
                   'https://lh3.googleusercontent.com'
                   '/InPgClcuGiNA5TdEGTu7zuGSv1LDJ54L_sC49G7fqJ0YawDcdmN78t7iShcrbyQ_sdoUyjyBAoXVMTKaaf9OP8ekDyBaEEWJMiDbi8M=s120',
                   'https://lh3.googleusercontent.com'
                   '/c_wASW_EH06TmUJTAfZ9HYAx8rhKbu3SbOqpHHp0OistKOTJcPDjhSBg3S6OM3HG9ivBpVVtSnKkNJKilZQCc_8V1kTG7JQDSzmWoQ=s120',
                   'https://lh3.googleusercontent.com/UoABiu1ydkR50jb_G2BPJO1I9dQ30o6DzRY2RCPoo'
                   '-etNtb77FRj2WxoxG_sYL6C6I5qiu88g6BpAX6GfIGjuFPcZQ_beA_M8TWpQDM=s120',
                   'https://lh3.googleusercontent.com/BMCuX'
                   '-_CakY3bKgjl7mxVgAKKug2D1xdWNcenSeKYReZtIfYGD1Uo0BN7nIeDtRIsgu6Xz8b90AYGCqn8EvKWhaiHJ2-OVu0Oos-NA'
                   '=s120',
                   'https://lh3.googleusercontent.com'
                   '/5tHPLRm3oJiR0xNSIuBvZthmH2bOC81QC2AE6N6tnV1xBzqV8h2QQDJb6IErqEiUp4CEUlUOvcxjB3NDKAajCocluKd577H1u2LU3es=s120']

    btn_list = []
    for (slug, url) in zip(slugs, image_links):
        btn = html.Button(id=f'{slug}', className="col-btn", children=[html.Img(src=f'{url}')])
        btn_list.append(btn)
    return html.Div(btn_list, className="collection_buttons")


def get_collection(offset, limit, slug):
    """
    Get assets belonging to a certain collection of NFTs, based on the collection id and pagination
    :param offset: offset for the request, calculated by page number
    :param limit: the number of assets fetched per page
    :param slug: collection slug, identifying property belonging to a specific collection
    :return: a dataframe containing data about each NFT
    """
    url = "https://api.opensea.io/api/v1/assets"
    querystring = {"offset": f"{offset}", "limit": f"{limit}", "collection": f"{slug}"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.json_normalize(data['assets'])
    # only need a certain set of columns
    col_list = ['id', 'token_id', 'image_url', 'name', 'asset_contract.address', 'collection.name']
    df = pd.DataFrame(df, columns=col_list)
    return df


def create_card(card_img, card_title, token_id, asset_contract_address):
    """

    :param card_img:
    :param card_title:
    :param token_id:
    :param asset_contract_address:
    :return: a card containing information about a specific NFT
    """
    asset_link = dbc.CardLink("{name}".format(name=card_title),
                              href="/asset?asset_contract_address={address}&token_id={token_id}".format(
                                  address=asset_contract_address, token_id=token_id), className="card-link")
    return dbc.Card(
        [
            dbc.CardImg(src=card_img, top=True),
            dbc.CardBody(
                [
                    html.H4(asset_link, className="card-title"),
                ],
                className="card-body",
            ),
        ],
        className="card border-primary col" #mb-3
    )


def create_cardgrid(offset, limit, slug):
    """
    Creates a grid of cards
    :param offset:
    :param limit:
    :param slug:
    :return: grid containing cards
    """
    data = get_collection(offset, limit, slug)
    cards = []
    for item in data.index:
        cards.append(create_card(data['image_url'][item], data['name'][item],
                                 data['token_id'][item], data['asset_contract.address'][item]))
    return data['collection.name'][0], html.Div(cards, className="col_card_grid row row-cols-4")


def create_layout():
    """
    Creates the layout for the collections page
    :return: layout with all the elements in
    """
    return html.Div(
        [
            dcc.Store(id='slug_memory'),  # local storage for collection slug value
            html.Div(
                [
                    html.H1('Collections', className="text-center"),
                    html.P('Utforsk noen utvalgte collections. Trykk på bildeknappene for å se samlingene', className="text-center"),
                    generate_img_buttons(),
                ],
                className="header",
            ),
            html.Div([
                html.H1(id="col_title", className="text-muted"),
                html.Div(id="col_pag"),
            ], className="d-md-flex flex-md-row justify-content-sm-between"),
            html.Div(id="collection_content"),
        ],
        className="main"
    )


@app.callback(
    Output("slug_memory", "data"),
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
def trigger_cardgrid(n_col1, n_col2, n_col3, n_col4, n_col5, n_col6):
    """
    Accepts click event from a image button, and prepares for the displaying of the card grid by saving the collection
    slug in the browser and setting up pagination controls
    :param n_col1: img_btn 1 click event
    :param n_col2: img_btn 2 click event
    :param n_col3: img_btn 3 click event
    :param n_col4: img_btn 4 click event
    :param n_col5: img_btn 5 click event
    :param n_col6: img_btn 6 click event
    :return: stores collection slug from image_btn in dcc.Store (localstorage),
    and outputs pagination element to the app layout
    """
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]  # get btn id for slug

    slug = button_id  # collection reference
    page_view = dbc.Pagination(max_value=5, first_last=True, active_page=1, id="collection_pagination",
                               className="pagination")
    return slug, page_view


@app.callback(Output("col_title", "children"),
              Output("collection_content", "children"),
              [Input("slug_memory", "data"), Input("collection_pagination", "active_page")])
def display_cardgrid(slug, page_no):
    """
    Create the cardgrid view based on slug, and output the cards to the app layout
    :param slug: collection slug used to identify the wanted collection
    :param page_no: current page number from pagination controls
    :return: card grid layout containing cards for all the assets, with pagination in mind
    """
    limit = 12
    page_no = page_no
    offset = (page_no * limit) - limit  # calculate offset
    return create_cardgrid(offset, limit, slug)
