from flask import redirect
import json, requests, webbrowser
import methods as m

def open_browser():
    try:
        url = 'http://127.0.0.1:5000/'
        webbrowser.open(url)
    except Exception:
        print('You need to manually open your browser and navigate to: http://127.0.0.1:5000/')

def get_tokens():
    with open('tokens.json', 'r') as openfile:
        tokens = json.load(openfile)
    return tokens

def check_expiration(tokens):
    if tokens['expires_in'] < 100:
        return m.refresh_tokens
    
def get_track_uris():
    with open('track_uris.json', 'r') as openfile:
        track_uris = json.load(openfile)
    return track_uris

def get_analysed_track_uris():
    with open('audio_features.json', 'r') as openfile:
        audio_features = json.load(openfile)
    return audio_features

def get_track_ids():
    with open('track_ids.json', 'r') as openfile:
        track_ids = json.load(openfile)
    return track_ids

def get_playlist_urls():
    with open('playlist_urls.json', 'r') as openfile:
        playlist_urls = json.load(openfile)
    return playlist_urls

def add_tracks(tokens, playlist_id, tracks_list):
    uri = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}
    payload = {'uris': tracks_list}
    r = requests.post(uri, headers=headers, data=json.dumps(payload))
    
def shutdown_server(environ):
    # look for dev server shutdown function in request environment
    if not 'werkzeug.server.shutdown' in environ:
        raise RuntimeError('Not running the development server')
    environ['werkzeug.server.shutdown']() # call the shutdown function
    print('Shutting down server...')