from flask import request, session
from datetime import datetime, timedelta, date
import base64
import json, requests
import helpers as hp
import os

CLI_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLI_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIR_URI = os.getenv("SPOTIFY_REDIRECT_URI")
USER_ID = os.getenv("SPOTIFY_USER_ID")

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
MY_FOLLOWED_ARTISTS_URL = "https://api.spotify.com/v1/me/following?type=artist"
GET_ARTIST_ALBUMS_URL = "https://api.spotify.com/v1/artists"
MY_TOP_TRACKS_URL = "https://api.spotify.com/v1/me/top/tracks"
AUDIO_FEATURES = "https://api.spotify.com/v1/audio-features"

def get_top_tracks():
    tokens = hp.get_tokens()
    hp.check_expiration(tokens)
    
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    payload = {"limit":100}
    r = requests.get(MY_TOP_TRACKS_URL, headers=headers, params=payload)
    response = r.json()
    
    track_uris = []
    track_ids = []
    tracks = response['items']
    for track in tracks:
        track_uris.append(track['uri'])
        track_ids.append(track['id'])
        
    # accounting for next page
    while response['next']:
        next_page_uri = response['next']
        r = requests.get(next_page_uri, headers=headers)
        response = r.json()
        for track in response['items']:
            track_uris.append(track['uri'])
            track_ids.append(track['id'])
    
    uri_dict = {'uris': track_uris}
    with open('track_uris.json', 'w') as outfile:
        json.dump(uri_dict, outfile)
    id_dict = {'ids': track_ids}
    with open('track_ids.json', 'w') as outfile:
        json.dump(id_dict, outfile)
        
        
def analyse_tracklist():
    tokens = hp.get_tokens()
    hp.check_expiration(tokens)
    
    track_ids = hp.get_track_ids()['ids']
    track_ids = ','.join(track_ids)
    
    headers = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}
    payload = {'ids' : track_ids}
    r = requests.get(AUDIO_FEATURES, headers=headers, params=payload)
    response = r.json()
    
    track_data = []
    danceable_song_uris = []
    moody_song_uris = []
    happy_song_uris = []
    sad_song_uris = []
    
    for track in response['audio_features']:
        dict = {
            'uri' : track['uri'],
            'danceability' : track['danceability'],
            'valence' : track['valence']
        }
        track_data.append(dict)
        
    for track in track_data:
        track_uri = track['uri']
        if track['danceability'] >= 0.5:
            danceable_song_uris.append(track_uri)
        else:
            moody_song_uris.append(track_uri)
        
        if track['valence'] >= 0.5:
            happy_song_uris.append(track_uri)
        else:
            sad_song_uris.append(track_uri)
            
    audio_features_dict = {
        "danceable" : danceable_song_uris,
        "moody" : moody_song_uris,
        "happy" : happy_song_uris,
        "sad" : sad_song_uris
    }
    
    with open('audio_features.json', 'w') as outfile:
        json.dump(audio_features_dict, outfile)
    
def create_four_playlists(user):
    tokens = hp.get_tokens()
    playlist_name_array = ["Songs to Dance To", "Songs to Mope About", "Songs to Cheer You On", "Songs to feel Melodramatic To"]
    USER_ID = user
    playlist_ids = []
    playlist_urls = []
    
    uri = f'https://api.spotify.com/v1/users/{USER_ID}/playlists'
    headers = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}
    for name in playlist_name_array:
        payload = {
            'name': name,
            'description': f'Created from {USER_ID} top 100 songs.'
        }
        r = requests.post(uri, headers=headers, data=json.dumps(payload))
        response = r.json()
        playlist_ids.append(response['id'])
        playlist_urls.append(response['external_urls']['spotify'])
    
        session['playlist_ids'] = playlist_ids
        session['playlist_urls'] = playlist_urls
    
    with open('playlist_urls.json', 'w') as outfile:
        json.dump(playlist_urls, outfile)
    
    print(f'{r.status_code} - Created 4 playlists!')
    
def add_to_four_playlists():
    tokens = hp.get_tokens()
    playlist_ids = session['playlist_ids']
    track_uris = hp.get_analysed_track_uris()
    
    hp.add_tracks(tokens, playlist_ids[0], track_uris['danceable'])
    hp.add_tracks(tokens, playlist_ids[1], track_uris['moody'])
    hp.add_tracks(tokens, playlist_ids[2], track_uris['happy'])
    hp.add_tracks(tokens, playlist_ids[3], track_uris['sad'])
        
    print("Added tracks to playlist!")
    
    playlist_urls = hp.get_playlist_urls()
    print(playlist_urls)
    result = {
        "Danceable": playlist_urls[0],
        "Moody": playlist_urls[1],
        "Happy": playlist_urls[2],
        "Sad": playlist_urls[3]
    }
    
    return result


def get_artists():
    
    tokens = hp.get_tokens()
    hp.check_expiration(tokens)
        
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    r = requests.get(MY_FOLLOWED_ARTISTS_URL, headers=headers)
    response = r.json()
    
    artist_ids = []
    artists = response['artists']['items']
    for artist in artists:
        artist_ids.append(artist['id'])
        
    # accounting for next page
    while response['artists']['next']:
        next_page_uri = response['artists']['next']
        r = requests.get(next_page_uri, headers=headers)
        response = r.json()
        for artist in response['artists']['items']:
            artist_ids.append(artist['id'])
    
    print("Received artist IDs")
    session['artist_ids'] = artist_ids
    
def get_albums():
    tokens = hp.get_tokens()
    artist_ids = session['artist_ids']
    
    album_ids = []
    album_names = {}
    
    today = datetime.now()
    number_weeks = timedelta(weeks=4)
    timeframe = (today - number_weeks).date()
    
    for id in artist_ids:
        uri = f'{GET_ARTIST_ALBUMS_URL}/{id}/albums?include_groups=album,single&country=US'
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        r = requests.get(uri, headers=headers)
        response = r.json()
        
        albums = response['items']
        for album in albums:
            try:
                release_date = datetime.strptime(album['release_date'], '%Y-%m-%d') #convert release date to datetime
                album_name = album['name']
                artist_name = album['artists'][0]['name']
                
                if release_date.date() > timeframe:
                    if album_name not in album_names or artist_name != album_names[album_name]: #in case of same name album but diff artist
                        album_ids.append(album['id'])
                        album_names[album_name] = artist_name
            except ValueError:
                print(f'Release date found with format: {album["release_date"]}')
    
    session['album_ids'] = album_ids
    print("Retrieved album IDs")

def get_tracks():
    tokens = hp.get_tokens()
    album_ids = session['album_ids']
    
    track_uris = []
    debug_response = {}
    
    for id in album_ids:
        uri = f'https://api.spotify.com/v1/albums/{id}/tracks'
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        r = requests.get(uri, headers=headers)
        response = r.json()
        
        tracks = response["items"]
        for track in tracks:
            track_uri = track["uri"]
            track_uris.append(track_uri)
        
        debug_response[id] = response
    
    print("Retrieved tracks!")
    
    uri_dict = {'uris': track_uris}
    with open('track_uris.json', 'w') as outfile:
        json.dump(uri_dict, outfile)

def create_playlist(user):
    tokens = hp.get_tokens()
    current_date = (date.today()).strftime('%m-%d-%Y')
    playlist_name = f'New Monthly Releases - {current_date}'
    
    USER_ID = user
    
    uri = f'https://api.spotify.com/v1/users/{USER_ID}/playlists'
    headers = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}
    payload = {
        'name': playlist_name,
        'description': f'Monthly Recommendations for {USER_ID}'
    }
    r = requests.post(uri, headers=headers, data=json.dumps(payload))
    response = r.json()
    
    session['playlist_id'] = response['id']
    session['playlist_url'] = response['external_urls']['spotify']
    
    print(f'{r.status_code} - Created playlist!')

def add_to_playlist():
    tokens = hp.get_tokens()
    playlist_id = session['playlist_id']
    track_uris = hp.get_track_uris()
    tracks_list = track_uris['uris']
    number_of_tracks = len(tracks_list)
    
    #if track list > 200
    if number_of_tracks > 200:
        three_split = np.array_split('tracks_list', 3)
        for list in three_split:
            hp.add_tracks(tokens, playlist_id, list(list))
    elif number_of_tracks > 100:
        two_split = np.array_split('tracks_list', 2)
        for list in two_split:
            hp.add_tracks(tokens, playlist_id, list(list))     
    else:
        hp.add_tracks(tokens, playlist_id, tracks_list)
        
    print("Added tracks to playlist!")
    
    return session['playlist_url']
            
def refresh_tokens():
    tokens = hp.get_tokens()
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token']
    }
    
    base64encoded = str(base64.b64encode(f'{CLI_ID}:{CLIE_SECRET}'.encode('ascii')), 'ascii')
    headers = {
        'Authorization': f'Basic {base64encoded}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    r = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)
    response = r.json
    
    tokens = {
        'access_token': response['access_token'],
        'refresh_token': tokens['refresh_token'],
        'expires_in': response['expires_in']
    }
    
    with open('tokens.json', 'w') as outFile:
        json.dump(tokens, outFile)
        
    print("Tokens refreshed successfully")
    get_artists()