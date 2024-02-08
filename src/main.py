import os
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import requests
from dotenv import load_dotenv
import paramiko

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
local_dir_variable = os.getenv("local_dir")
remote_dir_variable = os.getenv("remote_dir")
audio_filename = None

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
        try:
            os.remove("album_art.jpg")
        except:
            print("No artwork found")
        print("Album art added to the MP3 file and album_art.jpeg deleted.")
    except error:
        print("Failed to add album art to the MP3 file.")

def download_audio(url):
    global audio_filename
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

def connect_ssh(user, host, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host, port=8022, username=user, password=password)
        sftp = ssh.open_sftp()
        local_dir = local_dir_variable + audio_filename
        remote_dir = remote_dir_variable + audio_filename
        sftp.put(local_dir, remote_dir)
        print("Succesfully transfered file!")
    except paramiko.AuthenticationException:
        print("Failed to login. Verify username/password")
    finally:
        ssh.close()

if __name__ == "__main__":
    url = input("URL of Youtube video: ")
    download_audio(url)
    local_file = audio_filename
    connect_ssh(os.getenv("user"), os.getenv("host"), os.getenv("password"))
