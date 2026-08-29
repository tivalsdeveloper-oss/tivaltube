from tivaltube import download, download_audio, get_info

URL = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

print(get_info(URL)["title"])
download(URL, quality="720p")
download_audio(URL, audio_format="mp3")

