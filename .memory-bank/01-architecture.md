# Architecture

## Core Components

### Main Entry Point

- **`main.py`**: Primary script containing all core functionality
  - Argument parsing and configuration
  - Course fetching and processing
  - Download orchestration
  - File management

### Authentication & Session Management

- **`tls.py`**: Custom SSL/TLS adapter for fingerprinting
  - `SSLCiphers` class: Custom HTTP adapter with configurable cipher suites
- **`Session` class** (in main.py): HTTP session wrapper
  - Handles visit requests for Cloudflare cookies
  - Retry logic for failed requests
- **`UdemyAuth` class** (in main.py): Authentication handler
  - Supports bearer tokens and browser cookie extraction

### Course Data Extraction

- **`Udemy` class** (in main.py): Main API interaction class
  - Course information extraction
  - Curriculum parsing
  - Lecture/asset extraction
  - M3U8 and MPD stream parsing
  - Subtitle extraction

### DRM & Decryption

- **`utils.py`**: KID (Key ID) extraction from MP4 files
  - `extract_kid()`: Extracts Widevine PSSH data from encrypted MP4 files
- **`mp4parse.py`**: MP4 box parsing for PSSH extraction
- **`widevine_pssh_data_pb2.py`**: Protocol buffer definitions for Widevine PSSH data
- **`keyfile.json`**: User-provided decryption keys (KID -> Key mapping)

### Utilities

- **`constants.py`**: Configuration constants
  - API endpoints
  - Headers and authentication
  - File paths
  - Logging configuration
- **`vtt_to_srt.py`**: Subtitle format conversion
  - Converts WebVTT to SRT format

## Data Flow

1. **Initialization**
   - Parse command-line arguments
   - Setup logging
   - Load decryption keys from `keyfile.json`
   - Initialize session with authentication

2. **Course Discovery**
   - Extract portal name and course name from URL
   - Fetch user's subscribed courses
   - Match course by name or ID

3. **Curriculum Fetching**
   - Fetch curriculum items (chapters, lectures, quizzes)
   - Handle pagination
   - Parse lecture assets and metadata

4. **Content Processing**
   - For each lecture:
     - Determine if encrypted (DRM) or unencrypted
     - Extract video sources (HLS, DASH, or direct)
     - Extract subtitles
     - Extract supplementary assets
   - For quizzes:
     - Fetch quiz data
     - Generate HTML templates

5. **Download Process**
   - **Unencrypted videos**: Direct download via aria2c
   - **Encrypted videos (DRM)**:
     - Download encrypted video/audio segments via yt-dlp
     - Extract KID from downloaded files
     - Lookup decryption key from keyfile
     - Decrypt and mux using ffmpeg
   - **Captions**: Download and convert VTT to SRT
   - **Assets**: Download files, presentations, e-books, etc.

## External Dependencies

### Required System Tools

- **ffmpeg**: Video processing, decryption, and muxing
- **aria2c**: High-performance downloader
- **shaka-packager**: DASH stream processing (though not actively used in current code)
- **yt-dlp**: Video stream extraction and downloading

### Python Packages

See `requirements.txt` for full list. Key dependencies:

- `requests`: HTTP client
- `yt-dlp`: Video downloader wrapper
- `m3u8`: HLS playlist parsing
- `browser_cookie3`: Browser cookie extraction
- `protobuf`: Protocol buffer support for Widevine
- `beautifulsoup4`: HTML parsing
- `coloredlogs`: Enhanced logging
