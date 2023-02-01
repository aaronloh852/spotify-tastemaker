from flask import Flask, redirect, render_template, request
from dotenv import load_dotenv
import helpers as hp
import methods as m
import requests
import os
import json

load_dotenv()

CLI_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLI_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIR_URI = os.getenv("SPOTIFY_REDIRECT_URI")
USER_ID = os.getenv("SPOTIFY_USER_ID")

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
MY_FOLLOWED_ARTISTS_URL = "https://api.spotify.com/v1/me/following?type=artist"
GET_ARTIST_ALBUMS_URL = "https://api.spotify.com/v1/artists"

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

hp.open_browser()

@app.route('/')
def home():
    """Homepage"""
    return render_template('index.html')

@app.route('/get_auth')
def request_auth():
    # Auth flow step 1 - request authorization
    scope = 'user-top-read playlist-modify-public playlist-modify-private user-follow-read'
    return redirect(f'https://accounts.spotify.com/authorize?client_id={CLI_ID}&response_type=code&redirect_uri={REDIR_URI}&scope={scope}')
    
    
@app.route("/callback")
def load_page(): 
    # Get code from response url, code is the prefix
    code = request.args.get('code')
    return render_template('loading.html', code=code)    

@app.route("/fetchdata/<code>")
def fetch_data(code):
    
    # construct payload for HTTP POST request
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIR_URI,
        'client_id': CLI_ID,
        'client_secret': CLI_SECRET
    }
    
    r = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    response = r.json() # parse json
    
    tokens = {
        'access_token': response['access_token'],
        'refresh_token': response['refresh_token'],
        'expires_in': response['expires_in']
    }
    
    with open('tokens.json', 'w') as outFile:
        json.dump(tokens, outFile)
    
    
    return redirect('/loading')
    
@app.route('/loading')
def loading():
    m.get_top_tracks()
    m.analyse_tracklist()
    m.create_four_playlists(USER_ID)
    url_dict = m.add_to_four_playlists()
    a = url_dict['Danceable']
    b = url_dict['Moody']
    c = url_dict['Happy']
    d = url_dict['Sad']
    return render_template('final.html', dance=a, moody=b,
                           happy=c, sad=d)
    
   

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)