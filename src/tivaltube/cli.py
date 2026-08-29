"""Command-line interface for TivalTube."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .downloader import Downloader, DownloadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tivaltube", description="Download authorized YouTube media")
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument("-o", "--output", default="downloads", help="output directory")
    parser.add_argument("-q", "--quality", default="best", help="best, 1080p, 720p, etc.")
    parser.add_argument("--audio", action="store_true", help="extract audio instead of video")
    parser.add_argument("--audio-format", default="mp3", choices=["mp3", "m4a", "opus", "wav", "flac"])
    parser.add_argument("--playlist", action="store_true", help="download the complete playlist")
    parser.add_argument("--subtitles", action="store_true", help="save English subtitles when available")
    parser.add_argument("--info", action="store_true", help="print metadata without downloading")
    parser.add_argument("--cookies-from-browser", help="browser name, such as firefox or chrome")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    downloader = Downloader(
        Path(args.output),
        cookies_from_browser=args.cookies_from_browser,
    )
    try:
        if args.info:
            info = downloader.info(args.url)
            print(json.dumps({k: info.get(k) for k in ("id", "title", "uploader", "duration", "webpage_url")}, indent=2))
        elif args.playlist:
            results = downloader.playlist(args.url, quality=args.quality)
            print(f"Downloaded {len(results)} playlist item(s).")
        elif args.audio:
            result = downloader.audio(args.url, audio_format=args.audio_format)
            print(f"Downloaded: {result.title}")
        else:
            result = downloader.video(args.url, quality=args.quality, subtitles=args.subtitles)
            print(f"Downloaded: {result.title}")
        return 0
    except (DownloadError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
