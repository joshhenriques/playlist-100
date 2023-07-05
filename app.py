import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, url_for, session, request, redirect, render_template_string, render_template
import urllib.request
import json
import time
import os, shutil
import pandas as pd
from dataProcessing import makeData
from config import cid, secret

app = Flask(__name__)

app.secret_key = 'OIUHs9w8zqJSHd112' #Random string for session
app.config['SESSION_COOKIE_NAME'] = 'Joshs Cookie'
app.config['UPLOAD_FOLDER'] = os.path.join('static' , 'Images')
app.config["TEMPLATES_AUTO_RELOAD"] = True

TOKEN_INFO = "token_info"

@app.route('/')
def index():
    #Add Login buttoN

    #Removes images in folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if(filename[0] == 'a'): #Only deletes albums
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    sp = create_spotify_oauth()
    auth_url = sp.get_authorize_url()

    return render_template("index.html", url=auth_url)
    # return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp.get_access_token(code)
    session[TOKEN_INFO] = token_info

    return redirect(url_for('getData', _external = True))

@app.route('/getData')
def getData():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    
    #Iterate to get multiple songs
    sp = spotipy.Spotify(auth = token_info['access_token'])
    uris = makeData(sp)
    import random

    random.shuffle(uris)
    uris = uris[:10]
    session['uris'] = uris

    return redirect(url_for('songs', uris = uris, _external = True))

@app.route('/songs')
def songs():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")

    sp = spotipy.Spotify(auth = token_info['access_token'])
    uris = request.args['uris']
    uris = session['uris']
    
    trackURLs = []
    imageURLS = []
    imagePaths = []
    trackNames = []
    artists=[]
    for uri in uris:
        trackURLs.append("https://open.spotify.com/track/" + uri)
        
        track = sp.track(track_id=uri)
        trackName = track['name']
        if(len(trackName) > 25):
            trackName = trackName[:25] + "..."


        trackNames.append(trackName)

        imageURL = track['album']['images'][1]['url']
        imageURLS.append(imageURL)
        imageName = "album" + uri
        imagePath = os.path.join(app.config['UPLOAD_FOLDER'], imageName)
        imagePaths.append(imagePath)
        urllib.request.urlretrieve(imageURL, imagePath)
        # print(track['album']['images'])

        
        artist = ""
        for i in range(len(track['artists'])):
            artist += track['artists'][i]['name'] + ', '
        artist = artist.rsplit(',' , 1)[0]
        artists.append(artist)
        
        #print(trackName)
        # print(artists)
    
    return render_template(
        "songs.html",  
        albumImg1 = imagePaths[0], link1 = trackURLs[0], name1 = trackNames[0], artist1 = artists[0],
        albumImg2 = imagePaths[1], link2 = trackURLs[1], name2 = trackNames[1], artist2 = artists[1],
        albumImg3 = imagePaths[2], link3 = trackURLs[2], name3 = trackNames[2], artist3 = artists[2],
        albumImg4 = imagePaths[3], link4 = trackURLs[3], name4 = trackNames[3], artist4 = artists[3],
        albumImg5 = imagePaths[4], link5 = trackURLs[4], name5 = trackNames[4], artist5 = artists[4],
        albumImg6 = imagePaths[5], link6 = trackURLs[5], name6 = trackNames[5], artist6 = artists[5],
        albumImg7 = imagePaths[6], link7 = trackURLs[6], name7 = trackNames[6], artist7 = artists[6],
        albumImg8 = imagePaths[7], link8 = trackURLs[7], name8 = trackNames[7], artist8 = artists[7],
        albumImg9 = imagePaths[8], link9 = trackURLs[8], name9 = trackNames[8], artist9 = artists[8],
        albumImg10= imagePaths[9], link10 = trackURLs[9],name10= trackNames[9], artist10 = artists[9],
    )

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        sp = create_spotify_oauth()
        token_info = sp.refresh_access_token(token_info['refresh_token'])
    
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= cid,
        client_secret= secret,
        redirect_uri=url_for('redirectPage', _external = True),
        scope = "user-top-read"
    )
