# Data preparation

## Extract data directly from Spotify (no code)
In order to get all the information that Spotify has on us, we need to log into our account and 
go to Privacy settings.

Scroll down until you find something like "Download data" and follow the steps. An e-mail should 
be on your inbox in no more than 30 days.

You'll receive a lot of JSON files but the one we need is **Playlist.json** (in my case was 
`Playlist1.json`)

## Extracting songs from a playlist
_Description of the steps on **`get_playlist_songs.py`**_

I wanted to take a JSON file into a friendly CSV file :hugs:, to do that I need the **`json`** 
and **`pandas`** libraries

```Python
import json 
import pandas as pd
```

A JSON file is _something like_ a Python dictionary. The first key I needed was **'playlists'**. 
The value from **'playlists'** is a list of dictionaries. The element I was interested about 
was the first one: a compilation of all my #SpotifyWrap from 2016 to 2021 (the songs that 
were with me the entire time I was in college). That first element is a dictionary so, the second 
key I needed was **'items'** :arrow_right: a list of dictionaries (song's information)

```Python
with open('../data_spotify/Playlist1.json') as json_file:
    data = json.load(json_file)
    data = data['playlists']
    top100s = data[0]
    top100s_songs = top100s['items']
```

Some dictionaries (elements of **`top100s_songs`**) had **`None`** in **'track'**, those 
instances were some kind of short videos. So I got rid-off them.

```Python
def filter_song_attributes(element):
    if element['track'] != None:
        return element['track']

top100s_songs = list( map(filter_song_attributes,top100s_songs) )
```

I was almost done, I just needed to store all the information as a dictionary where every 
atributte is a key containing a list of values:

```
data = {
    'attribute_01': [a1, b1, c1, d1, e1],
    'attribute_02': [a1, b2, c2, d2, e2],
    ...
    'attribute_n': [an, bn, cn, dn, en]
}
```

:arrow_down:

```Python
list_trackName = [song['trackName'] for song in top100s_songs if song]
list_artistName = [song['artistName'] for song in top100s_songs if song]
list_albumName = [song['albumName'] for song in top100s_songs if song]
list_trackURI = [song['trackUri'] for song in top100s_songs if song]
dict_songs_100s = dict(name=list_trackName, artist=list_artistName, album=list_albumName, URI=list_trackURI)
```

The attribute **'trackUri'** is the one I used in the next script. Finally, save the dictionary 
as a **`pandas.DataFrame`**

```Python
df = pd.DataFrame(dict_songs_100s)
df['URI'] = df['URI'].str.split(':', expand=True).iloc[:,-1]
df.to_csv('../data/songs_my_top_100_2016-2021.csv', index=False)
```

## Extracting songs attributes