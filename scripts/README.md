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
Once I had all the songs and their **URI**, I could extract the 
[**audio features**](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features) 
from each song.

Before jumping into the code, I needed a **CLIENT ID** and a **CLIENT SECRET**. I got both by 
creating a New App in my Developer's Spotify Account.

Now it's time for [**Spotipy**](https://spotipy.readthedocs.io/en/2.19.0/). This library has many 
functionalities but I used some of them:

* Extract audio features.
* Extract track information.
* Extract information from the artist.

### Load data from the previous procedure and extract URIs
```Python
import numpy as np
import pandas as pd

data_songs = pd.read_csv('YOUR/PATH/DATA.csv')
arr_uris = data_songs['URI'].values
```

### Create a `spotipy.client.Spotify` object
To extract all the necessary information I had to create a 
**`spotipy.client.Spotify`** named **`spoti`**. Remember the **CLIENT ID** and 
**CLIENT SECRET**? Well, it's time to use them.

```Python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_cred_manager = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)
spoti = spotipy.Spotify(client_credentials_manager=client_cred_manager)
```
### Extract audio features
In order to extract the audio features I passed chunk (I have more than 500 songs in the 
playlist) of URIs the function **`spoti.audio_features()`**. If you have less than 100 you can 
pass all the URIs.

```Python
song_features_01 = spoti.audio_features(arr_uris[:100])
# ...
song_features_n = spoti.audio_features(arr_uris[last_idx:])
```

The **`song_features_`** variables are lists so, I added all the lists to get one list with 
all the audio features of every playlist's song. This variables is **`song_features`**. Each element
of this list is a dictionary with almost all the audio features of interest.

### Create a dictionary of audio features
Same case as the last procedure:
```Python
dict_audio_features = dict(id = [], danceability = [], energy = [], key = [], loudness = [], mode = [],
                           speechiness = [], acousticness = [], instrumentalness = [], liveness = [],
                           valence = [], tempo = [], duration_ms = [], time_signature = [],
                           artist_popularity = [])
```
then, I iterated over **`song_features`** and stored all the information in the dictionary.

```Python
for song_info in song_features:
    for key in song_info:
        if key in list(dict_audio_features.keys()):
            dict_audio_features[key].append(song_info[key])
```

You can see that there are is an extra attribute called **`artist_popularity`**, to obtain this 
attribute I had to extract the artist's ID from each track

```Python
for uri in arr_uris:
    dict_track = spoti.track(uri)
    artistID = dict_track['artists'][0]['id']
    dict_audio_features['artist_popularity'].append(spoti.artist(artist_id=artistID)['popularity'])
```

### Final `panda.DataFrame`

```Python
data_audio_features = pd.DataFrame(dict_audio_features)
```

and before saving all the information as a CSV file, I merged  **`data_songs`** with **`data_audio`**

```Python
df = pd.merge(left=data_songs, right=data_audio_features, left_on='URI', right_on='id')
df.drop(columns='id',inplace=True)
df.to_csv('../data/songs_atributtes_my_top_100_2016-2021.csv', index=False)
```