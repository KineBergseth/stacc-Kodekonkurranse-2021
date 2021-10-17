# Stacc - Kodekonkurranse 2021

A app where you can view NFTs, put inn fake offers and upload your own NFTs (they do not get uploaded for real).
The asset cards have links in the name, that takes you to a page displaying a single asset.

Disclaimer: the marketplace may be a bit wonky sometimes, if some links are broken the cards will be text only,
try refreshing or messing around with the filter to get assets with data available :)

The webapp can be viewed here: 
https://stacc-nft.herokuapp.com/

## Getting started 
The app is written in Python with Dash framework. The app is also available on heroku.
If you want to run it locally follow the steps below:

###Prerequisites
- Python 3.X 
- Internet connection

###Setup
Start by opening your preferred terminal, and navigate to this project's directory.
To be able to run the code, you need to install the required python modules.
You install the required libraries by writing the following in your terminal:

```
pip install -r requirements.txt
```

#### Running the code
```
python index.py
```

The Dash app should now be running on http://127.0.0.1:8050/, and you must open up that address in a browser of your choice.


OpenSea API was used for the project:
https://docs.opensea.io/reference/api-overview
