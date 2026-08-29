"""TivalTube public API."""

from .downloader import (
    Downloader,
    DownloadError,
    DownloadResult,
    download,
    download_audio,
    download_playlist,
    get_info,
)

__all__ = [
    "DownloadError",
    "DownloadResult",
    "Downloader",
    "download",
    "download_audio",
    "download_playlist",
    "get_info",
]
__version__ = "0.1.0"
