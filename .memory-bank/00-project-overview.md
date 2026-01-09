# Project Overview

## Purpose

A Python-based utility for downloading Udemy courses with support for DRM-protected content. The tool can download lectures, captions, quizzes, and supplementary assets from Udemy courses.

## Key Features

- **DRM Support**: Can decrypt and download DRM-protected videos (requires user-provided decryption keys)
- **Multiple Content Types**: Downloads lectures, captions, quizzes, articles, and supplementary assets
- **Quality Selection**: Allows specifying video quality or automatically selects best available
- **Multiple Formats**: Supports HLS, DASH, and direct video downloads
- **Caption Support**: Downloads and converts VTT captions to SRT format
- **Chapter Filtering**: Can download specific chapters using range notation
- **H.265 Encoding**: Optional video re-encoding with H.265 codec
- **Browser Cookie Extraction**: Can extract authentication cookies from various browsers

## Legal Disclaimer

⚠️ **Important**:

- Downloading courses violates Udemy's Terms of Service
- Tool requires user-provided decryption keys (not provided by the project)
- Use at your own risk - account suspension is possible
- Project is provided as-is with no warranty

## Repository

Based on the original work by Puyodead1: <https://github.com/Puyodead1/udemy-downloader>

## Credits

- Original codebase: <https://github.com/Jayapraveen/Drm-Dash-stream-downloader>
- PSSH extraction: <https://github.com/alastairmccormack/pywvpssh>
- MP4 parsing: <https://github.com/alastairmccormack/pymp4parse>
- VTT to SRT conversion: <https://github.com/lbrayner/vtt-to-srt>
- Udemy API information: <https://github.com/r0oth3x49/udemy-dl>
