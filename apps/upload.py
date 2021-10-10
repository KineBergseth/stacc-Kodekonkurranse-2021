import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
from dash import dcc
import datetime


def make_json():
    asset = {
      "id": 68079114,
      "token_id": "67222163736366812115248145867153913994637167072440910807912450046197447524353",
      "image_url": "https://lh3.googleusercontent.com/RsvSnb3pzST8amJoNRiydKLFPNG2NPQhNc1fkvBY1yhAVMc6iYOGa6AobIrVE6t6Rt6TgDHdfwx3pbq17oLyqQkZmxLNlBo7NhBLz8M",
      "name": "The Crypto Ape#529",
      "description": "The Crypto Ape #529, enjoying its life in the Ethereum Blockchain!",
      "asset_contract": {
        "address": "0x495f947276749ce646f68ac8c248420045cb7b5e",
        "asset_contract_type": "semi-fungible",
        "created_date": "2020-12-02T17:40:53.232025",
        "name": "Stacc Collection",
        "owner": 102384,
        "schema_name": "ERC1155",
        "symbol": "OPENSTORE"
      },
      "owner": {
        "user": {
          "username": "NullAddress"
        }
      }
    }
    return asset

#test_base64 =


upload_img = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-image-upload'),
])

def parse_contents(contents, filename, date):
    print(contents)
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

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
            upload_img,
        ],
        className="main"

    )

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children