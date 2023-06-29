import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import pandas as pd
from tabulate import tabulate
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity  
from sklearn.metrics.pairwise import sigmoid_kernel
import numpy as np

def makeData(sp):

    #Keys in ['items']
    # ["album","artists","available_markets","disc_number","duration_ms","explicit",
    # "external_ids","external_urls","href","id","is_local","name","popularity",
    # "preview_url", "track_number","type","uri"]

    # song_uri = long_term[0]['uri'].split(':')[-1]
    # sp.audio_features(song_uri)[0]

    i=0
    j=0
    lt_complete = False
    mt_complete = False
    st_complete = False

    lt_uris = []
    mt_uris = []
    st_uris = []

    lt_features = []
    mt_features = []
    st_features = []

    genres = []

    #Only working w short term data for now
    while True:
        # if (lt_complete and mt_complete and st_complete):
        #     break

        if st_complete: break
        if mt_complete: break

        #Get top tracks over long term, medium term and short term
        # if not lt_complete: long_term = sp.current_user_top_tracks(limit=20,offset = i*20,time_range="long_term")['items']
        if not mt_complete: medium_term = sp.current_user_top_tracks(limit=20,offset = i*20,time_range="medium_term")['items']
        #if not st_complete: short_term = sp.current_user_top_tracks(limit=20,offset = i*20,time_range="short_term")['items']

        # if len(long_term) < 20: lt_complete = True
        if len(medium_term) < 20: mt_complete = True
        #if len(short_term) < 20: st_complete = True

        # for item in long_term:
        #     lt_uris += [item['uri'].split(':')[-1]]
        #     lt_features += [sp.audio_features(item['uri'].split(':')[-1])]
        for item in medium_term: 
            artistName = item['album']['artists'][0]['name'] 
            track = sp.search(artistName)['tracks']['items'][0]
            artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
            genres += artist['genres']
            # print(artistName , " Genre: " , artist['genres'])
            mt_features += sp.audio_features(item['id'])

        i += 1
        # for item in short_term:
        #     st_uris += [item['uri'].split(':')[-1]]
        #     st_features += sp.audio_features(item['uri'].split(':')[-1])
    
    from collections import Counter
    # genres.sort(key=Counter(genres).get, reverse=True)
    genreDict = {}
    for genre in set(genres):
        genreDict[genre] = genres.count(genre)

    mt_dataFrame = pd.DataFrame(mt_features)
    mt_dataFrame = mt_dataFrame.drop(mt_dataFrame.columns[14:], axis=1)  #Holds the data to reccomend song
    mt_dataFrame = mt_dataFrame.drop(mt_dataFrame.columns[11:13], axis=1) 

    songs = genRecommendations(mt_dataFrame, genreDict)
    # print(st_dataFrame)
    return songs

def genRecommendations(df, genreDict):

    #Organize CSV data to have same format as df
    # spotify_df = pd.read_csv('tracks.csv')
    # spotify_df = spotify_df.drop(spotify_df.columns[19], axis = 1)
    # spotify_df = spotify_df.drop(spotify_df.columns[1:8], axis = 1)

    spotify_df = pd.read_csv('dataset.csv')
    datasetGenres = spotify_df['track_genre']
    spotify_df = spotify_df.drop(spotify_df.columns[2:8], axis = 1)
    spotify_df = spotify_df.drop(spotify_df.columns[0], axis = 1)
    spotify_df = spotify_df.drop(spotify_df.columns[12:], axis = 1)
    spotify_df = spotify_df.rename(columns={'track_id' : 'uri'})

    feature_cols=['danceability','energy','key', 'loudness', 'mode','speechiness','acousticness',
                  'instrumentalness', 'liveness', 'valence','tempo']
    
    #Scale Data
    scaler = MinMaxScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    spotify_df[feature_cols] = scaler.fit_transform(spotify_df[feature_cols])

    weightedVector = genWeightedVector(df)
    
    # df.info()
    # Create cosine model

    spotify_df['sim'] = cosine_similarity(spotify_df[feature_cols], weightedVector.reshape(1,-1))
    topSongs = spotify_df.sort_values('sim', ascending=False).head(10)
   
    return str(topSongs['uri'])

def genWeightedVector(df):

    feature_cols=['danceability','energy','key', 'loudness', 'mode','speechiness','acousticness',
                  'instrumentalness', 'liveness', 'valence','tempo']
    
    weightedVector = [0]*len(feature_cols)

    for i, row in df.iterrows():
        ind = 0
        for feature in feature_cols:
            weightedVector[ind] += row[feature] / len(df.index)
            ind+=1

    return np.array(weightedVector)


spotify_df = pd.read_csv('dataset.csv')
# spotify_df.info()
spotify_df = spotify_df.drop(spotify_df.columns[2:8], axis = 1)
spotify_df = spotify_df.drop(spotify_df.columns[0], axis = 1)
spotify_df = spotify_df.drop(spotify_df.columns[12:], axis = 1)
spotify_df = spotify_df.rename(columns={'track_id' : 'uri'})
# spotify_df = spotify_df.drop(spotify_df.columns[19], axis = 1)
# spotify_df = spotify_df.drop(spotify_df.columns[19], axis = 1)
# spotify_df = spotify_df.drop(spotify_df.columns[1:8], axis = 1)

feature_cols=['danceability','energy','key', 'loudness', 'mode','speechiness','acousticness',
                  'instrumentalness', 'liveness', 'valence','tempo']
import random
vector = []
for r in range(11):
    vector.append(random.random())

spotify_df['sim'] = cosine_similarity(spotify_df[feature_cols], np.array(vector).reshape(1,-1))
topSongs = spotify_df.sort_values('sim', ascending=False).head(5)

# print(topSongs)