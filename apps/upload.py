import dash
from app import app
import datetime
import json
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL


# test_base64 =


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


def create_layout():
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




@app.callback(
    Output("output_upload", "children"),
    [Input("upload_btn", "n_clicks")]
)
def add_favourite(n_upload, image_url, name, description):
    if n_upload:
        upload_asset = {
            "id": 68079114,  # generate
            "token_id": "67222163736366812115248145867153913994637167072440910807912450046197447524353", # generate
            "image_url": image_url,
            "name": name,
            "description": description,
            "asset_contract": {
                "address": "0x495f947276749ce646f68ac8c248420045cb7b5e", # generate
                "asset_contract_type": "semi-fungible",
                "created_date": "2020-12-02T17:40:53.232025", # get current time/date
                "name": "Stacc Collection",
                "owner": 102384,
                "schema_name": "ERC1155",
                "symbol": "OPENSTORE"
            },
            "owner": {
                "user": {
                    "username": "lizardlover23"
                }
            }
        }
        write_json(upload_asset, 'uploaded_nfts', 'uploads.json')
        return "wohoo"


def write_json(new_json, name, filename):
    with open(filename, 'r+') as file:
        # print(new_json)
        file_data = json.load(file)  # load data into dict
        # print(file_data)
        # if new_json not in file_data:
        file_data[name].append(new_json)
        file.seek(0)
        json.dump(file_data, file, indent=4)
        # TODO dont allow duplicates