"""
Extract the songs from a Spotify playlist. 

Data stored in Playlist1.json
"""
# L I B R A R I E S
import json
import pandas as pd

# F U N C T I O N S
def filter_song_attributes(element):
    if element['track'] != None:
        return element['track']

# C O D E
with open('../data_spotify/Playlist1.json') as json_file:
    data = json.load(json_file)
    data = data['playlists']
    top100s = data[0] # Select the playlist
    top100s_songs = top100s['items']

top100s_songs = list(map(filter_song_attributes,top100s_songs))

list_trackName = [song['trackName'] for song in top100s_songs if song]
list_artistName = [song['artistName'] for song in top100s_songs if song]
list_albumName = [song['albumName'] for song in top100s_songs if song]
list_trackURI = [song['trackUri'] for song in top100s_songs if song]
dict_songs_100s = dict(name=list_trackName, artist=list_artistName, album=list_albumName,URI=list_trackURI)

df = pd.DataFrame(dict_songs_100s)
df['URI'] = df['URI'].str.split(':', expand=True).iloc[:,-1]
df.to_csv('../data/songs_my_top_100_2016-2021.csv', index=False)