import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, url_for, session, request, redirect
import json
import time
import pandas as pd
from dataProcessing import makeData

cid = '813271a905464bdd8521413ab9037a84'
secret = '5b9fc690517a4da9a00646653e23e8b3'

app = Flask(__name__)

app.secret_key = 'OIUHs9w8zqJSHd112' #Random string for session
app.config['SESSION_COOKIE_NAME'] = 'Joshs Cookie'
TOKEN_INFO = "token_info"

@app.route('/')
def index():
    #Add Login button
    sp = create_spotify_oauth()
    auth_url = sp.get_authorize_url()

    return redirect(auth_url)

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

    return makeData(sp)

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
        client_id='813271a905464bdd8521413ab9037a84',
        client_secret='5b9fc690517a4da9a00646653e23e8b3',
        redirect_uri=url_for('redirectPage', _external = True),
        scope = "user-top-read"
    )
