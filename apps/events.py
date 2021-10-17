import dash_bootstrap_components as dbc
import requests
import dash
import pandas as pd
from dash.exceptions import PreventUpdate
from dash import html, dash_table, Input, Output
from app import app


def convert_price(wei):
    """
    convert wei to ETH
    :param url: wei amount
    :return: ETH amount
    """
    return wei / pow(10, 18)


def add_imgmarkdown(url):
    """
    Add html to link to display image
    :param url: NFT image link
    :return: link in html element
    """
    return "<img src='{url}' height='75' />".format(url=url)


def get_events(event_type):
    url = f"https://api.opensea.io/api/v1/events?event_type={event_type}&only_opensea=false&offset=0&limit=30"
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers)
    data = response.json()

    df = pd.json_normalize(data['asset_events'])
    df = pd.DataFrame(df)
    col_list = ['asset.image_url', 'asset.name', 'event_type', 'ending_price']
    df = pd.DataFrame(df, columns=col_list)
    df['asset.image_url'] = df['asset.image_url'].apply(add_imgmarkdown)
    df['ending_price'] = df['ending_price'].astype(float)
    df['ending_price'] = df['ending_price'].apply(convert_price)
    pd.set_option('display.max_colwidth', None)  # extend colwidth to display whole value, instead of partial values
    return df


def generate_table(data):
    return dash_table.DataTable(
        id='table',
        data=data.to_dict('records'),
        columns=[
            {"id": "asset.image_url", "name": "NFT", "presentation": "markdown"},
            {"id": "asset.name", "name": "Item"},
            {"id": "ending_price", "name": "Price ETH"},
            {"id": "event_type", "name": "Event"},
        ],
        markdown_options={"html": True},
        sort_action='native',
        style_header={},
        style_cell={'textAlign': 'left', "whiteSpace": "pre-line"},
        style_as_list_view=True,
        editable=False,
    )


def create_layout():
    """
    Creates the layout for the home page
    :return: layout with all the elements in
    """

    return html.Div(
        [
            html.Div(
                [
                    html.H1('Activity', id='header-text text-center mt-3'),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Listings", id="created", outline=True, color="primary"),
                            dbc.Button("Sales", id="successful", outline=True, color="primary"),
                            dbc.Button("Bids", id="bid_entered", outline=True, color="primary"),
                            dbc.Button("Transfers", id="transfer", outline=True, color="primary"),
                        ]
                    )
                ],
                className="header",
            ),
            html.Div(id="event_list"),
        ],
        className="main"
    )


@app.callback(
    Output("event_list", "children"),
    [Input("created", "n_clicks"),
     Input("successful", "n_clicks"),
     Input("bid_entered", "n_clicks"),
     Input("transfer", "n_clicks")]
)
def update_table(n_listings, n_sales, n_bids, n_transfers):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]  # get btn id for slug
        print(button_id)
        data = get_events(button_id)
        return generate_table(data)
