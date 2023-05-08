import pandas as pd
import requests
from datetime import datetime, timezone
from unidecode import unidecode
from pathlib import Path
import json

def get_igdb_data(igdb_id):
    '''Takes an IGDB game id number
    
    Returns list on genres, platform, and rating for the given game'''
    game_data = requests.get(f'https://api.igdb.com/v4/games/{igdb_id}?fields=genres.name,platforms.name,total_rating',
                         headers=headers)

    try:
        genres = [genre['name'] for genre in game_data.json()[0]['genres']]
    except KeyError:
        genres = []

    try:    
        platforms = [platform['name'] for platform in game_data.json()[0]['platforms']]
    except KeyError:
        platforms = []

    try:
        rating = int(round(game_data.json()[0]['total_rating'], 0))
    except KeyError:
        rating = 0 

    return genres, platforms, rating

#loading json file with API data
with open('./config.json', 'r') as f:
    config = json.load(f)

#Getting Twitch access token
payload = {
    "client_id": config['Twitch']['client_id'],
    "client_secret": config['Twitch']['client_secret'],
    "grant_type": "client_credentials"
}
response = requests.post("https://id.twitch.tv/oauth2/token", data=payload)
access_token = response.json()["access_token"]

#creating headers variable for api call
headers = {
    "Client-ID": config['Twitch']['client_id'],
    "Authorization": f"Bearer {access_token}"   
}

#Reading dataset with Twitch game data
df = pd.read_csv('./game_dataset.csv')

game_ids = df['igdb_id'].unique()
igdb_data = pd.DataFrame(columns=['igdb_id', 'genres', 'platforms', 'rating'])

#Calling IGDB API for each game ID from the Twitch data dataset
for game_id in game_ids:
    genre, platform, rating = get_igdb_data(game_id)
    igdb_data = pd.concat([igdb_data, pd.DataFrame(data={'igdb_id': game_id,
                         'genres': [genre],
                         'platforms': [platform],
                         'rating': rating})])
    
#exploding the dataset
igdb_data = igdb_data.explode('genres').explode('platforms').reset_index(drop=True)

#saving the IGDB dataset
filepath = Path(f'./igdb_data.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
igdb_data.to_csv(filepath, index=False)