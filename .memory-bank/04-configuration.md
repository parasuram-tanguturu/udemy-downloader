# Configuration Guide

## Initial Setup

### 1. Environment Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
# - ffmpeg (recommended: yt-dlp team's custom build)
# - aria2c
# - shaka-packager
# - yt-dlp (can use pip or system package)
```

### 2. Configuration Files

#### `keyfile.json`

Create from `keyfile.example.json`:

```json
{
  "kid1": "decryption_key1",
  "kid2": "decryption_key2"
}
```

- KID: Key ID extracted from video files (hex string)
- Key: Decryption key for that KID (hex string)
- Required for DRM-protected courses

#### `.env` (Optional)

```env
UDEMY_BEARER=your_bearer_token_here
```

- Alternative to passing bearer token via command line

## Command-Line Arguments

### Required

- `-c, --course-url`: Course URL to download

### Authentication

- `-b, --bearer`: Bearer token (or use `.env` or `--browser`)
- `--browser`: Extract cookies from browser (chrome, firefox, opera, edge, brave, chromium, vivaldi, safari)

### Download Options

- `-q, --quality`: Specific video quality (e.g., 720, 1080)
- `-l, --lang`: Caption language (default: "en", use "all" for all languages)
- `-cd, --concurrent-downloads`: Max concurrent segment downloads (1-30, default: 10)
- `--skip-lectures`: Skip video downloads
- `--skip-hls`: Skip HLS streams (faster, but may miss 1080p for non-DRM)
- `--download-assets`: Download supplementary assets
- `--download-captions`: Download captions/subtitles
- `--download-quizzes`: Download quizzes
- `--keep-vtt`: Keep VTT files after SRT conversion
- `--chapter`: Filter specific chapters (e.g., "1,3-5,7")

### Output Options

- `-o, --out`: Output directory (default: `out_dir`)
- `--id-as-course-name`: Use course ID instead of name (for long paths)
- `-n, --continue-lecture-numbers`: Continuous numbering across chapters

### Video Encoding

- `--use-h265`: Re-encode videos with H.265 codec
- `--h265-crf`: CRF value for H.265 (default: 28)
- `--h265-preset`: Preset for H.265 (default: "medium")
- `--use-nvenc`: Use NVIDIA hardware encoding (requires CUDA-enabled ffmpeg)

### Caching

- `--save-to-file`: Cache course data to JSON files
- `--load-from-file`: Load course data from cached JSON files

### Information

- `--info`: Print course information only (no downloads, slow - parses each lecture)
- `--curriculum-only`: Generate only `curriculum.md` file (fast, no detailed parsing)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Subscription Courses

- `-sc, --subscription-course`: Mark course as subscription-based

## Output Structure

```
out_dir/
└── Course Name/
    ├── curriculum.md          # Automatically generated course curriculum
    └── 01 - Chapter Name/
        ├── 001 Lecture Title.mp4
        ├── 001 Lecture Title_en.srt
        ├── 001 Lecture Title_es.srt
        ├── 001 asset.pdf
        ├── 002 Lecture Title.mp4
        └── quiz.html
```

**Note**: The `curriculum.md` file is automatically generated in the course directory and contains comprehensive course metadata, chapter structure, lecture details, DRM status, available qualities, captions, assets, and quiz information. It is generated both during downloads and when using `--info` mode.

## Logging

- **Console**: Colored output with timestamps
- **File**: `logs/YYYY-MM-DD-HH-MM-SS.log`
- **Format**: `[timestamp] [logger] [function:line] LEVEL: message`

## Directory Structure

- `out_dir/`: Default download directory
- `saved/`: Cached course data
- `logs/`: Log files
- `temp/`: Temporary M3U8/MPD files (cleaned up after use)

## System Requirements

### Minimum

- Python 3.x
- ffmpeg
- aria2c
- shaka-packager
- yt-dlp

### Recommended

- Custom ffmpeg build from yt-dlp team (for better compatibility)
- NVIDIA GPU with CUDA (for hardware encoding with `--use-nvenc`)

## Authentication Methods

### Method 1: Bearer Token

1. Extract from browser DevTools
2. Use `-b` flag or `.env` file
3. See README for browser-specific instructions

### Method 2: Browser Cookies

1. Use `--browser chrome` (or other browser)
2. Program extracts cookies automatically
3. Useful for subscription courses

### Method 3: Cookie File

1. Export cookies to `cookies.txt` (Netscape format)
2. Use `--browser file`

## Troubleshooting

### Missing Keys

- Error: "Audio key not found for {kid}"
- Solution: Extract KID from video file, add to `keyfile.json`

### Authentication Failures

- Check bearer token is valid
- For subscription courses, may need cookies instead
- Try `--browser` flag

### Download Failures

- Check system tools are in PATH
- Verify network connectivity
- Check log files for detailed errors

### Path Length Issues (Windows)

- Use `--id-as-course-name` to shorten paths
- Or use `-o` to specify shorter output path
