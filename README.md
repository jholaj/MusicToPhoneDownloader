
# Music to Phone Downloader

- Downloads .mp3 from YouTube URL
- If found on Spotify, assign metadata
- Transfer file via SSH to phone ([Setup](https://gist.github.com/raveenb/ab3217798c827be889b83b584d70b08b))


## Prerequisites

#### pip install

```http
  paramiko
  yt_dlp
  spotipy
  mutagen
```
#### .env file

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `SPOTIPY_CLIENT_ID` | `string` |  Your Spotify Client ID from [dashboard](https://developer.spotify.com/dashboard) |
| `SPOTIPY_CLIENT_SECRET` | `string` | Your Spotify Client Secret from [dashboard](https://developer.spotify.com/dashboard) |
| `host` | `string` | SSH host name |
| `user` | `string` | SSH user name |
| `password` | `string` | SSH password |
| `local_dir` | `string` | Local directory where is file downloaded, e.g. C:\\\Music\\\ |
| `remote_dir` | `string` | Remote directory where is file downloaded, e.g. storage/music/ |


