# TivalTube

TivalTube is a small Python library and terminal command for downloading YouTube media that you own or have permission to save. It uses `yt-dlp` as its download engine.

## Install

From this project folder:

```bash
python -m pip install .
```

Install FFmpeg for combining high-quality video/audio and converting MP3 files:

```bash
sudo apt update
sudo apt install ffmpeg
```

## Python examples

```python
from tivaltube import download, download_audio, download_playlist, get_info

url = "https://www.youtube.com/watch?v=VIDEO_ID"

info = get_info(url)
print(info["title"])

video = download(url, output_dir="my_videos", quality="720p")
print(video.files)

audio = download_audio(url, output_dir="my_music", audio_format="mp3")
print(audio.title)

items = download_playlist(
    "https://www.youtube.com/playlist?list=PLAYLIST_ID",
    output_dir="playlists",
    quality="1080p",
)
print(f"Downloaded {len(items)} videos")
```

For progress updates:

```python
from tivaltube import Downloader

def progress(status):
    if status["status"] == "downloading":
        print(status.get("_percent_str", ""), status.get("_speed_str", ""))
    elif status["status"] == "finished":
        print("Download finished; processing media...")

downloader = Downloader("downloads", progress=progress)
downloader.video("https://www.youtube.com/watch?v=VIDEO_ID", quality="720p")
```

## Terminal examples

```bash
tivaltube "VIDEO_URL" --quality 720p
tivaltube "VIDEO_URL" --audio --audio-format mp3
tivaltube "PLAYLIST_URL" --playlist --quality 1080p
tivaltube "VIDEO_URL" --subtitles
tivaltube "VIDEO_URL" --info
```

Some age-restricted or account-authorized content may require your own browser session:

```bash
tivaltube "VIDEO_URL" --cookies-from-browser firefox
```

Never share exported cookies. YouTube changes regularly, so keep the engine current:

```bash
python -m pip install --upgrade yt-dlp
```

## Run tests

```bash
python -m pip install -e ".[dev]"
pytest
```

## Responsible use

Only download content you own, content licensed for download, or content whose owner has given permission. Follow copyright law, YouTube's terms, and any applicable access restrictions.

Powered by tivalsdeveloper.

