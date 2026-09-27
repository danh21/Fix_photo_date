# Fix Photo Date

## 📚 Table of Contents

- [Fix Photo Date](#fix-photo-date)
  - [📚 Table of Contents](#-table-of-contents)
  - [📝 About](#-about)
  - [📁 Source](#-source)
  - [🚀 Getting Started](#-getting-started)
    - [💻 Technology](#-technology)
    - [🛠️ Build / Verification](#️-build--verification)
  - [🔗 Reference](#-reference)

## 📝 About

Fix Photo Date is a desktop application for updating JPEG photo and MP4 video dates from timestamps in their filenames.

- Includes a manual mode for setting the same date and time on JPG/JPEG images and MP4 videos directly inside a selected folder, without relying on filenames.
- Writes the date to the EXIF `DateTime`, `DateTimeOriginal`, and `DateTimeDigitized` fields.
- Writes the date to the MP4 `©day` metadata tag.
- Updates the file's modified and access timestamps.
- Creates an optional `.bak` backup before changing each image.
- Provides a dry-run option to review matching photos without modifying them.

For example, `IMG_UPLOAD_20230422_103446.jpg` is interpreted as April 22, 2023 at 10:34:46.

## 📁 Source

```
.
├── src/
│   ├── filename_dates.py       # Filename timestamp parsers
│   ├── manual_datetime.py      # Parser for manually entered date and time
│   ├── main.py                 # Tkinter application and workflow
│   └── photo_metadata.py       # JPEG EXIF and filesystem date updates
├── test/
│   ├── test_filename_dates.py  # Filename parser unit tests
│   └── test_manual_datetime.py # Manual date-time input tests
├── doc/                        # Additional documentation
├── rsc/                        # Project resources
└── README.md
```

## 🚀 Getting Started

### 💻 Technology

- Python 3.10 or later
- Tkinter for the desktop interface (included with most Python installations)
- Pillow for JPEG image handling
- piexif for EXIF metadata updates
- Mutagen for MP4 metadata updates
- Python `unittest` for filename parser tests

### 🛠️ Build / Verification

Install the required image libraries from the project root:

```bash
python -m pip install -r requirements.txt
```

Start the application:

```bash
python src/main.py
```

Run the tests:

```bash
python -m unittest discover -s test -v
```

The application scans JPG/JPEG and MP4 files in the selected folder. It currently recognizes these filename timestamps:

```text
YYYYMMDD_HHMMSS
YYYYMMDD-HHMMSS
FB_IMG_<UNIX_TIMESTAMP_MS>
received_<UNIX_TIMESTAMP_US>
```

For example, `FB_IMG_1488170740397.jpg` contains a Unix timestamp in milliseconds and `received_1638770899781207.jpeg` contains a Unix timestamp in microseconds. The latter resolves to December 6, 2021 at 06:08:19.781207 UTC. The application displays and writes these timestamps using the computer's local timezone. Each filename format is handled by a separate parser in `src/filename_dates.py`, so additional formats can be added independently.

To set a date manually, open the **Sửa thủ công** (Manual Edit) tab, choose a folder, and enter the desired local date and time as `YYYY-MM-DD HH:MM:SS`. Click **Sửa tất cả ảnh trong thư mục** and confirm. The shared backup and Dry run options also apply. JPG/JPEG and MP4 files directly inside the selected folder are processed; subfolders are not scanned.

## 🔗 Reference
