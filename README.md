# Spotify Taste Maker

## About
This is an app that is meant to run on your computer locally once. It uses the Spotify Web API to retrieve your top 100 songs and sieves them into different playlists based on the mood and tone of the songs to create themed playlists.

Built using Python, Flask and Figma

## Installation
Ensure that you have Python3 installed. 
Register an application on the [Spotify developer dashboard](https://developer.spotify.com/dashboard).

Clone this repository and fill in the .env fields appropriately.
```
SPOTIFY_CLIENT_ID= (Retrieved from Spotify develloper application dashboard)
SPOTIFY_CLIENT_SECRET= (Retrieved from Spotify develloper application dashboard)
SPOTIFY_REDIRECT_URI= 'http://127.0.0.1:5000/callback' (Set the redirect URI on the dashboard to this URI)
SPOTIFY_USER_ID= (Your spotify account username)
SECRET_KEY= (Can be created with the following command: python -c 'import secrets; print(secrets.token_hex())')
```

## Setup
Create a virtual environment within the directory and run it:
```
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:
```
pip install -r requirements.txt
```

Specify the flask app:
```
export FLASK_APP=tastemaker.py
```

Run the app:
```
flask run
```

## Screenshots
![Main Page](/screenshots/screenshot.png)