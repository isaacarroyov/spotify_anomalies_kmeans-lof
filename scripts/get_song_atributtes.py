import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

clientID = 'CLIENT_ID'
clientSecret = 'CLIENT_SECRET'

data_songs = pd.read_csv('YOUR/PATH/DATA.csv')
arr_uris = data_songs['URI'].values

client_cred_manager = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)
spoti = spotipy.Spotify(client_credentials_manager=client_cred_manager)

song_features = spoti.audio_features(arr_uris[:100])

# Or this 
#song_features_01 = spoti.audio_features(arr_uris[:100])
#song_features_02 = spoti.audio_features(arr_uris[100:200])
#song_features_03 = spoti.audio_features(arr_uris[200:300])
#song_features_04 = spoti.audio_features(arr_uris[300:400])
#song_features_05 = spoti.audio_features(arr_uris[400:500])
#song_features_06 = spoti.audio_features(arr_uris[500:])
#song_features = song_features_01 + song_features_02 + song_features_03 + song_features_04 + song_features_05 + song_features_06

dict_audio_features = dict(id = [], danceability = [], energy = [], key = [], loudness = [], mode = [], speechiness = [], acousticness = [],
instrumentalness = [], liveness = [], valence = [], tempo = [], duration_ms = [], time_signature = [], artist_popularity = [])

for uri in arr_uris:
    dict_track = spoti.track(uri)
    artistID = dict_track['artists'][0]['id']
    dict_audio_features['artist_popularity'].append(spoti.artist(artist_id=artistID)['popularity'])

for song_info in song_features:
    for key in song_info:
        if key in list(dict_audio_features.keys()):
            dict_audio_features[key].append(song_info[key])

data_audio_features = pd.DataFrame(dict_audio_features)

df = pd.merge(left=data_songs, right=data_audio_features, left_on='URI', right_on='id')
df.drop(columns='id',inplace=True)
df.to_csv('YOUR/PATH/DATA.csv', index=False)