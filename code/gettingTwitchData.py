import pandas as pd
import requests
from datetime import datetime, timezone
from unidecode import unidecode
from pathlib import Path
import json

#loading json file with API data
with open('./config.json', 'r') as f:
    config = json.load(f)

#Getting Twitch access token
url = "https://id.twitch.tv/oauth2/token"
payload = {
    "client_id": config['Twitch']['client_id'],
    "client_secret": config['Twitch']['client_secret'],
    "grant_type": "client_credentials"
}
response = requests.post(url, data=payload)
access_token = response.json()["access_token"]

#creating headers variable for api call
headers = {
    "Client-ID": config['Twitch']['client_id'],
    "Authorization": f"Bearer {access_token}"
}

#creating an empty df where values will be stored
games = pd.DataFrame(data=[], columns=['id', 'igdb_id','twitch_id', 'name', 'datetime', 'view_count'])

#getting top 20 streams
game_response = requests.get("https://api.twitch.tv/helix/games/top?first=20", headers=headers)
top_games = game_response.json()["data"]

record_datetime = datetime.now(tz=timezone.utc)

for game in top_games:
    #skipping non-gaming streams
    if game['igdb_id']=='':
        continue
     
    #getting data from ongoing live streams
    stream_response = requests.get(f"https://api.twitch.tv/helix/streams?game_id={game['id']}&first=100&type=live",
                                   headers=headers)
    
    view_count=sum(stream['viewer_count'] for stream in stream_response.json()['data'])
    unique_id = game['igdb_id']+ '_' + str(record_datetime.month) + '_' + str(record_datetime.day) + '_' + str(record_datetime.hour)
    
    temp = pd.DataFrame(data={'id': unique_id, 
                              'igdb_id':game['igdb_id'],
                              'twitch_id':game['id'],
                              'name':unidecode(game['name']),
                              'datetime': record_datetime,
                              'view_count':view_count},
                        index=[int(game['igdb_id'])])

    games = pd.concat([games, temp])

filepath = Path(f'./games_{record_datetime.date()}_{record_datetime.hour}.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
games.to_csv(filepath, index=False)