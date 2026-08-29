from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tivaltube import Downloader


def test_quality_formats():
    assert Downloader._video_format("best") == "bv*+ba/b"
    assert "720" in Downloader._video_format("720p")
    with pytest.raises(ValueError):
        Downloader._video_format("ultra")


def test_video_download_returns_result(tmp_path: Path):
    fake_info = {
        "id": "abc123",
        "title": "Demo",
        "webpage_url": "https://www.youtube.com/watch?v=abc123",
        "requested_downloads": [{"filepath": str(tmp_path / "Demo.mp4")}],
    }
    client = MagicMock()
    client.__enter__.return_value.extract_info.return_value = fake_info
    with patch("tivaltube.downloader.yt_dlp.YoutubeDL", return_value=client):
        result = Downloader(tmp_path).video("https://www.youtube.com/watch?v=abc123", quality="720p")
    assert result.title == "Demo"
    assert result.video_id == "abc123"
    assert result.files == (tmp_path / "Demo.mp4",)


def test_invalid_audio_format(tmp_path: Path):
    with pytest.raises(ValueError):
        Downloader(tmp_path).audio("https://example.invalid", audio_format="exe")

