from app import app
import datetime
import json
import string
import secrets
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output


def create_layout():
    """
    Create layout, input form for image, name and description of a NFT
    :return: html to render content
    """
    upload_nft_img = html.Div([
        dcc.Upload(
            id='upload-nft-img',
            children=html.Div([
                'Drag & drop or ',
                html.A('Select file to upload')
            ]),
            style={
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            className=".w-50 mb-3",
            multiple=False
        )
    ])

    name_input = html.Div(
        [
            dbc.Label("Name"),
            dbc.Input(type="text", id="nft-name", placeholder="Enter name"),
        ],
        className="mb-3",
    )

    desc_input = html.Div(
        [
            dbc.Label("Description"),
            dbc.Input(
                type="text",
                id="nft-desc",
                placeholder="Enter description",
            ),
        ],
        className="mb-3",
    )

    input_form = dbc.Form([name_input, desc_input])

    return html.Div(
        children=[
            html.Div(
                html.H1('Upload NFT', className='header-text text-center mt-3'),
                className="header",
            ),
            upload_nft_img,
            input_form,
            dbc.Button(
                "Upload", id="upload_nft", className="ml-auto", n_clicks=0,
            ),
            html.Div(id='nft-data-upload'),

        ],
        className="main"
    )


def random_data_gen(length):
    """
    Generate random metadata using secure random string. With cryptography no string generated will be the same result
    :param length: length of generated string
    :return: randomized string containing letters and numbers
    """
    metadata = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(length))
    return str(metadata)


@app.callback(
    Output("nft-data-upload", "children"),
    [Input("upload_nft", "n_clicks"),
     Input("nft-name", "value"),
     Input("nft-desc", "value"),
     Input('upload-nft-img', 'contents')
     ]
)
def add_nft(n_upload, name, description, image_url):
    """
    Add NFT to local json file with all data
    :param n_upload: upload button click event
    :param name: name input from formgroup
    :param description: description of NFT
    :param image_url: base64 encoded image
    :return: html to render img and table with recap of inputted and generated data
    """
    if n_upload:
        if image_url is None:
            return html.P("Please upload nft file")
        else:
            nft_id = random_data_gen(8)  # generate data
            token_id = random_data_gen(60)
            contract_address = f"0x{random_data_gen(40)}"
            date = datetime.now()  # get current time and date
            upload_asset = {
                "id": nft_id,
                "token_id": token_id,
                "image_url": image_url,
                "name": name,
                "description": description,
                "asset_contract": {
                    "address": contract_address,
                    "asset_contract_type": "semi-fungible",
                    "created_date": str(date),
                    "name": "Stacc Collection",
                    "owner": 1920133,
                    "schema_name": "ERC1155",
                    "symbol": "STACC"
                },
                "owner": {
                    "user": {
                        "username": "lizardlover23"
                    }
                }
            }
            write_json(upload_asset, 'uploaded_nfts', 'uploads.json')

            # create table rows to display all NFT data in
            row1 = html.Tr([html.Td("id"), html.Td(upload_asset['id'])])
            row2 = html.Tr([html.Td("token id"), html.Td(upload_asset['token_id'])])
            row3 = html.Tr([html.Td("name"), html.Td(upload_asset['name'])])
            row4 = html.Tr([html.Td("description"), html.Td(upload_asset['description'])])
            row5 = html.Tr([html.Td("asset contract address"), html.Td(upload_asset['asset_contract']['address'])])
            row6 = html.Tr([html.Td("asset contract type"), html.Td(upload_asset['asset_contract']['asset_contract_type'])])
            row7 = html.Tr([html.Td("created_date"), html.Td(upload_asset['asset_contract']['created_date'])])
            row8 = html.Tr([html.Td("asset contract name"), html.Td(upload_asset['asset_contract']['name'])])
            row9 = html.Tr([html.Td("asset contract owner"), html.Td(upload_asset['asset_contract']['owner'])])
            row10 = html.Tr([html.Td("schema_name"), html.Td(upload_asset['asset_contract']['schema_name'])])
            row11 = html.Tr([html.Td("symbol"), html.Td(upload_asset['asset_contract']['symbol'])])
            row12 = html.Tr([html.Td("owner"), html.Td(upload_asset['owner']['user']['username'])])
            table_body = [html.Tbody([row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12])]
            return html.Div([
                html.Img(src=image_url, className=".w-50"),
                dbc.Table(table_body, bordered=True)
            ])


def write_json(new_json, name, filename):
    """
    Write NFT data as object to json file
    :param new_json: NFT in json format
    :param name: value of name in name_value par list
    :param filename: filename of file its stored in
    """
    with open(filename, 'r+') as file:
        file_data = json.load(file)  # load data into dict
        file_data[name].append(new_json)
        file.seek(0)
        json.dump(file_data, file, indent=4)
