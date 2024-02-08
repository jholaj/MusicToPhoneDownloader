import os
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import requests
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

def search_spotify(track_name):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = sp.search(q=track_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_name = track['album']['name']
        artist_name = track['artists'][0]['name']
        album_art_url = track['album']['images'][0]['url'] if track['album']['images'] else None
        return album_name, artist_name, album_art_url
    else:
        return None, None, None

def download_album_art(album_art_url):
    response = requests.get(album_art_url)
    if response.status_code == 200:
        with open("album_art.jpg", 'wb') as image_file:
            image_file.write(response.content)
            print("Album art downloaded successfully.")
    else:
        print("Failed to download album art.")

def add_album_art(audio_filename):
    try:
        audio_file = MP3(audio_filename, ID3=ID3)
        audio_file.tags.add(
            APIC(
                encoding=3,  # 3 = UTF-8
                mime='image/jpeg',
                type=3,  # 3 = album front cover
                desc=u'Cover',
                data=open("album_art.jpg", 'rb').read()  # Album art file
            )
        )
        audio_file.save()
        print("Album art added to the MP3 file.")
    except error:
        print("Failed to add album art to the MP3 file.")

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        track_name = info['title']
        album_name, artist_name, album_art_url = search_spotify(track_name)
        if album_art_url:
            print(f"Album: {album_name}\nArtist: {artist_name}")
            audio_filename, audio_file_extension = os.path.splitext(ydl.prepare_filename(info))
            audio_filename += ".mp3"            
            ydl.download([url])

            download_album_art(album_art_url)
            add_album_art(audio_filename)
        else:
            print("Album art not found.")

if __name__ == "__main__":
    url = input("Zadejte URL adresu YouTube videa: ")
    download_audio(url)
