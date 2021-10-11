import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from urllib.parse import urlparse, parse_qsl, urlencode
from app import app
from app import server
from apps import (
    home,
    marketplace,
    nft_collections,
    asset,
    profile,
    upload
)

from navbar import Navbar

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    Navbar(),
    html.Div(
        id="main-content"
    )
])


# Update page when navbar is used
@app.callback(Output("main-content", "children"),
              [Input("url", "pathname"), Input("url", "href")])
def display_page(path_name, path_href):
    if path_name == "/marketplace":
        return marketplace.create_layout(app)
    elif path_name == "/collections":
        return nft_collections.create_layout(app)
    elif path_name.startswith("/asset"):
        # get query string from url as dictionary
        parse_result = urlparse(path_href)
        params = parse_qsl(parse_result.query)
        state = dict(params)
        return asset.create_layout(state)
    elif path_name == "/profile":
        return profile.create_layout(app)
    elif path_name == "/upload":
        return upload.create_layout(app)
    else:
        return home.create_layout(app)


if __name__ == '__main__':
    app.run_server(debug=True)
