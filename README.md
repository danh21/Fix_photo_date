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

Fix Photo Date is a desktop application for updating JPEG photo dates from timestamps in their filenames.

- Writes the date to the EXIF `DateTime`, `DateTimeOriginal`, and `DateTimeDigitized` fields.
- Updates the file's modified and access timestamps.
- Creates an optional `.bak` backup before changing each image.
- Provides a dry-run option to review matching photos without modifying them.

For example, `IMG_UPLOAD_20230422_103446.jpg` is interpreted as April 22, 2023 at 10:34:46.

## 📁 Source

```
.
├── src/
│   ├── filename_dates.py       # Filename timestamp parsers
│   ├── main.py                 # Tkinter application and workflow
│   └── photo_metadata.py       # JPEG EXIF and filesystem date updates
├── test/
│   └── test_filename_dates.py  # Filename parser unit tests
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
- Python `unittest` for filename parser tests

### 🛠️ Build / Verification

Install the required image libraries from the project root:

```bash
python -m pip install Pillow piexif
```

Start the application:

```bash
python src/main.py
```

Run the tests:

```bash
python -m unittest discover -s test -v
```

The application scans JPG/JPEG files in the selected folder. It currently recognizes these filename timestamps:

```text
YYYYMMDD_HHMMSS
YYYYMMDD-HHMMSS
FB_IMG_<UNIX_TIMESTAMP_MS>
```

For example, `FB_IMG_1488170740397.jpg` contains a Unix timestamp in milliseconds and resolves to February 27, 2017 at 04:45:40.397 UTC. The application displays and writes this timestamp using the computer's local timezone. Each filename format is handled by a separate parser in `src/filename_dates.py`, so additional formats can be added independently.

## 🔗 Reference
