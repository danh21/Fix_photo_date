"""Update JPEG/MP4 date metadata and filesystem timestamps."""

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


def _set_mp4_datetime(path: str, photo_datetime: datetime) -> None:
    """Write an MP4 QuickTime date tag."""
    try:
        from mutagen.mp4 import MP4
    except ImportError as error:
        raise RuntimeError("MP4 support requires Mutagen. Run: pip install mutagen") from error

    video = MP4(path)
    video["©day"] = [photo_datetime.strftime("%Y-%m-%dT%H:%M:%S")]
    video.save()


def _set_jpeg_datetime(path: str, photo_datetime: datetime) -> None:
    """Write common JPEG EXIF date fields."""
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

        scene_type_tag = piexif.ExifIFD.SceneType
        scene_type = exif_data["Exif"].get(scene_type_tag)
        if isinstance(scene_type, int):
            if 0 <= scene_type <= 255:
                exif_data["Exif"][scene_type_tag] = bytes((scene_type,))
            else:
                del exif_data["Exif"][scene_type_tag]

        updated_exif = piexif.dump(exif_data)
        image.save(path, "jpeg", exif=updated_exif, quality="keep")


def set_photo_datetime(path: str, photo_datetime: datetime) -> None:
    """Set JPEG EXIF or MP4 date metadata and filesystem timestamps."""
    extension = os.path.splitext(path)[1].lower()
    if extension == ".mp4":
        _set_mp4_datetime(path, photo_datetime)
    elif extension in (".jpg", ".jpeg"):
        _set_jpeg_datetime(path, photo_datetime)
    else:
        raise ValueError("Only JPEG/JPG and MP4 are supported")

    timestamp = photo_datetime.timestamp()
    os.utime(path, (timestamp, timestamp))