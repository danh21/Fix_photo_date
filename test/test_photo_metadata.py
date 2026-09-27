"""Verify media date metadata updates."""

import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from photo_metadata import set_photo_datetime


class PhotoMetadataTests(unittest.TestCase):
    @patch("photo_metadata.os.utime")
    @patch("mutagen.mp4.MP4")
    def test_sets_mp4_date_tag_and_file_timestamps(self, mock_mp4, mock_utime):
        photo_datetime = datetime(2024, 3, 9, 18, 35, 35)
        video = MagicMock()
        mock_mp4.return_value = video

        set_photo_datetime("sample.MP4", photo_datetime)

        mock_mp4.assert_called_once_with("sample.MP4")
        video.__setitem__.assert_called_once_with(
            "©day", ["2024-03-09T18:35:35"]
        )
        video.save.assert_called_once_with()
        mock_utime.assert_called_once_with(
            "sample.MP4", (photo_datetime.timestamp(), photo_datetime.timestamp())
        )


if __name__ == "__main__":
    unittest.main()