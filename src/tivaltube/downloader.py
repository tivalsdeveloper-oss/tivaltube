"""High-level wrapper around yt-dlp."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yt_dlp

ProgressCallback = Callable[[Mapping[str, Any]], None]


class DownloadError(RuntimeError):
    """Raised when a download or information request fails."""


@dataclass(frozen=True)
class DownloadResult:
    """Details about a completed download."""

    title: str
    video_id: str
    webpage_url: str
    files: tuple[Path, ...]
    raw_info: Mapping[str, Any]


class Downloader:
    """Configurable downloader for videos, audio, playlists, and subtitles."""

    def __init__(
        self,
        output_dir: str | Path = "downloads",
        *,
        quiet: bool = False,
        progress: ProgressCallback | None = None,
        cookies_from_browser: str | None = None,
    ) -> None:
        self.output_dir = Path(output_dir).expanduser()
        self.quiet = quiet
        self.progress = progress
        self.cookies_from_browser = cookies_from_browser

    def _base_options(self) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        options: dict[str, Any] = {
            "outtmpl": str(self.output_dir / "%(title)s [%(id)s].%(ext)s"),
            "quiet": self.quiet,
            "noplaylist": True,
            "windowsfilenames": True,
        }
        if self.progress:
            options["progress_hooks"] = [self.progress]
        if self.cookies_from_browser:
            options["cookiesfrombrowser"] = (self.cookies_from_browser,)
        return options

    @staticmethod
    def _run(url: str, options: dict[str, Any], *, download: bool) -> dict[str, Any]:
        try:
            with yt_dlp.YoutubeDL(options) as client:
                info = client.extract_info(url, download=download)
                if info is None:
                    raise DownloadError("No information was returned for this URL.")
                return info
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(str(exc)) from exc

    def info(self, url: str) -> dict[str, Any]:
        """Return metadata without downloading media."""
        return self._run(url, self._base_options(), download=False)

    def video(
        self,
        url: str,
        *,
        quality: str = "best",
        subtitles: bool = False,
        subtitle_languages: Sequence[str] = ("en",),
    ) -> DownloadResult:
        """Download one video, optionally with subtitles."""
        options = self._base_options()
        options["format"] = self._video_format(quality)
        if subtitles:
            options.update(
                writesubtitles=True,
                writeautomaticsub=True,
                subtitleslangs=list(subtitle_languages),
                subtitlesformat="srt/best",
            )
        info = self._run(url, options, download=True)
        return self._result(info)

    def audio(self, url: str, *, audio_format: str = "mp3", quality: str = "192") -> DownloadResult:
        """Download one video's audio. FFmpeg is required for conversion."""
        allowed = {"mp3", "m4a", "opus", "wav", "flac"}
        if audio_format not in allowed:
            raise ValueError(f"audio_format must be one of: {', '.join(sorted(allowed))}")
        options = self._base_options()
        options.update(
            format="bestaudio/best",
            postprocessors=[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": quality,
                }
            ],
        )
        info = self._run(url, options, download=True)
        return self._result(info, forced_extension=audio_format)

    def playlist(self, url: str, *, quality: str = "best") -> list[DownloadResult]:
        """Download every available video in a playlist."""
        options = self._base_options()
        options.update(
            noplaylist=False,
            format=self._video_format(quality),
            outtmpl=str(
                self.output_dir / "%(playlist_title)s" / "%(playlist_index)03d - %(title)s [%(id)s].%(ext)s"
            ),
            ignoreerrors=True,
        )
        info = self._run(url, options, download=True)
        return [self._result(entry) for entry in info.get("entries", []) if entry]

    @staticmethod
    def _video_format(quality: str) -> str:
        if quality == "best":
            return "bv*+ba/b"
        normalized = quality.lower().removesuffix("p")
        if not normalized.isdigit() or int(normalized) <= 0:
            raise ValueError("quality must be 'best' or a height such as '720' or '1080p'")
        return f"bv*[height<={normalized}]+ba/b[height<={normalized}]"

    def _result(self, info: Mapping[str, Any], forced_extension: str | None = None) -> DownloadResult:
        files: list[Path] = []
        for item in info.get("requested_downloads", []):
            path = item.get("filepath") or item.get("filename")
            if path:
                files.append(Path(path))
        if not files and info.get("_filename"):
            path = Path(str(info["_filename"]))
            files.append(path.with_suffix(f".{forced_extension}") if forced_extension else path)
        return DownloadResult(
            title=str(info.get("title", "Unknown title")),
            video_id=str(info.get("id", "")),
            webpage_url=str(info.get("webpage_url", info.get("original_url", ""))),
            files=tuple(files),
            raw_info=info,
        )


def download(url: str, output_dir: str | Path = "downloads", **kwargs: Any) -> DownloadResult:
    """Download a single video using a temporary Downloader."""
    return Downloader(output_dir).video(url, **kwargs)


def download_audio(url: str, output_dir: str | Path = "downloads", **kwargs: Any) -> DownloadResult:
    """Download audio using a temporary Downloader."""
    return Downloader(output_dir).audio(url, **kwargs)


def download_playlist(url: str, output_dir: str | Path = "downloads", **kwargs: Any) -> list[DownloadResult]:
    """Download a playlist using a temporary Downloader."""
    return Downloader(output_dir).playlist(url, **kwargs)


def get_info(url: str) -> dict[str, Any]:
    """Return metadata without downloading media."""
    return Downloader(quiet=True).info(url)
