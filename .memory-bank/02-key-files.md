# Key Files Reference

## Core Files

### `main.py` (2165 lines)

**Purpose**: Main application entry point and core logic

**Key Functions**:

- `pre_run()`: Initialization, argument parsing, logger setup
- `main()`: Main execution flow
- `parse_new()`: Course processing and download orchestration
- `process_lecture()`: Individual lecture download handling
- `handle_segments()`: DRM-encrypted video download and decryption
- `mux_process()`: Video/audio muxing with optional H.265 encoding
- `download_aria()`: File download using aria2c
- `process_caption()`: Caption download and conversion
- `process_quiz()`: Quiz processing (normal and coding assignments)

**Key Classes**:

- `Udemy`: Main API interaction class
- `Session`: HTTP session wrapper
- `UdemyAuth`: Authentication handler

### `constants.py`

**Purpose**: Centralized configuration constants

**Key Constants**:

- `CLIENT_ID`, `CLIENT_SECRET`: Udemy API credentials
- `HEADERS`: Default HTTP headers mimicking Udemy Android app
- `URLS`: Class containing all API endpoint templates
- `CURRICULUM_ITEMS_PARAMS`: Query parameters for curriculum API
- File paths: `HOME_DIR`, `SAVED_DIR`, `KEY_FILE_PATH`, `LOG_DIR_PATH`

### `utils.py`

**Purpose**: DRM-related utilities

**Key Functions**:

- `extract_kid(mp4_file)`: Extracts Key ID from encrypted MP4 file
  - Parses MP4 boxes to find PSSH header
  - Extracts Widevine PSSH data
  - Returns content ID (KID) as hex string

### `tls.py`

**Purpose**: Custom SSL/TLS handling

**Key Classes**:

- `SSLCiphers`: Custom HTTPAdapter with configurable cipher suites
  - Used to avoid fingerprinting/detection
  - Sets custom SSL context

### `vtt_to_srt.py`

**Purpose**: Subtitle format conversion

**Key Functions**:

- `convert()`: Converts VTT files to SRT format

## Configuration Files

### `keyfile.json` (user-created)

**Purpose**: Stores decryption keys for DRM-protected content

**Format**:

```json
{
  "kid1": "key1",
  "kid2": "key2"
}
```

- Keys are hex strings
- KID (Key ID) is extracted from video files
- Key is the decryption key for that KID

### `keyfile.example.json`

**Purpose**: Template for keyfile.json

### `.env` (optional)

**Purpose**: Environment variables for bearer token

- `UDEMY_BEARER`: Bearer token for authentication

## Template Files

### `templates/article_template.html`

**Purpose**: HTML template for article-type lectures

### `templates/quiz_template.html`

**Purpose**: HTML template for normal quizzes

### `templates/coding_assignment_template.html`

**Purpose**: HTML template for coding assignment quizzes

## Generated Files

### `saved/course_content.json`

**Purpose**: Cached course curriculum data (when using `--save-to-file`)

### `saved/_udemy.json`

**Purpose**: Cached parsed course structure (when using `--save-to-file`)

### `logs/*.log`

**Purpose**: Application logs with timestamps

### `temp/index_*.m3u8` and `temp/index_*.mpd`

**Purpose**: Temporary HLS/DASH playlist files for processing

### `out_dir/{Course Name}/curriculum.md`

**Purpose**: Comprehensive course curriculum documentation in markdown format
- Automatically generated during course processing
- Contains full course metadata (title, ID, chapter/lecture counts)
- Lists all chapters with lecture details
- Includes DRM status, available qualities, captions, assets, and quiz information
- Generated in both download mode and info-only mode (`--info`)
