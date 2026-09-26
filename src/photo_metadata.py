"""Update JPEG EXIF date fields and filesystem timestamps."""

import os
from datetime import datetime

try:
    from PIL import Image
    import piexif
except ImportError as error:
    raise SystemExit(
        "Missing libraries. Run:\n"
        "pip install Pillow piexif"
    ) from error


def set_photo_datetime(path: str, photo_datetime: datetime) -> None:
    """Set common JPEG EXIF date fields and filesystem timestamps."""
    exif_datetime = photo_datetime.strftime("%Y:%m:%d %H:%M:%S").encode("ascii")

    with Image.open(path) as image:
        if image.format != "JPEG":
            raise ValueError("Only JPEG/JPG is supported")

        exif_bytes = image.info.get("exif", b"")
        try:
            exif_data = piexif.load(exif_bytes) if exif_bytes else {
                "0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None
            }
        except Exception:
            exif_data = {
                "0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None
            }

        exif_data["0th"][piexif.ImageIFD.DateTime] = exif_datetime
        exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_datetime
        exif_data["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_datetime

        updated_exif = piexif.dump(exif_data)
        image.save(path, "jpeg", exif=updated_exif, quality="keep")

    timestamp = photo_datetime.timestamp()
    os.utime(path, (timestamp, timestamp))