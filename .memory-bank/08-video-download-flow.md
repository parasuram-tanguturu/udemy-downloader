# Video Download Flow

This document explains how videos are downloaded from Udemy courses with detailed visual flow diagrams.

## Overview

The video download process differs based on whether the video is **DRM-protected** or **unencrypted**. This document covers both paths with step-by-step visual flows.

---

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START DOWNLOAD                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         Fetch Course Curriculum (API Call)                   │
│  GET /api-2.0/courses/{id}/subscriber-curriculum-items/     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Parse Course Structure                          │
│  • Extract chapters                                          │
│  • Extract lectures                                          │
│  • Extract lecture metadata                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         For Each Chapter → For Each Lecture                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Check DRM?   │
                    └──────┬───────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
    ┌───────────────┐           ┌───────────────┐
    │  DRM Video    │           │ Non-DRM Video │
    │   (Encrypted) │           │  (Unencrypted)│
    └───────┬───────┘           └───────┬───────┘
            │                           │
            │                           │
            ▼                           ▼
    [DRM Download Flow]        [Non-DRM Download Flow]
```

---

## Non-DRM Video Download Flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    NON-DRM VIDEO DOWNLOAD                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Parse Lecture Data                                      │
│ ─────────────────────────────────────────────────────────────── │
│ • Extract sources from lecture.asset.stream_urls.Video          │
│ • Parse HLS playlists (if --skip-hls not used)                  │
│ • Get all available quality sources                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Quality Selection                                       │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   Sources: [1080p, 720p, 480p, 360p, 144p]                     │
│                                                                  │
│   IF --quality specified:                                       │
│     ┌─────────────────────────────┐                            │
│     │ Find closest match to -q     │                            │
│     │ Example: -q 720 → 720p      │                            │
│     └─────────────────────────────┘                            │
│                                                                  │
│   ELSE:                                                          │
│     ┌─────────────────────────────┐                            │
│     │ Select highest quality       │                            │
│     │ Example: 1080p selected      │                            │
│     └─────────────────────────────┘                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Check Source Type                                       │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   ┌──────────────┐                    ┌──────────────┐         │
│   │  HLS Stream  │                    │ Direct Video │         │
│   │  (.m3u8)     │                    │   (.mp4)     │         │
│   └──────┬───────┘                    └──────┬───────┘         │
│          │                                    │                 │
│          │                                    │                 │
│          ▼                                    ▼                 │
│   ┌──────────────┐                    ┌──────────────┐         │
│   │  yt-dlp +    │                    │   aria2c     │         │
│   │  aria2c      │                    │   (direct)   │         │
│   └──────────────┘                    └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4A: HLS Stream Download (via yt-dlp)                      │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   yt-dlp Command:                                                │
│   ┌────────────────────────────────────────────────────┐       │
│   │ yt-dlp \                                           │       │
│   │   --enable-file-urls \                            │       │
│   │   --force-generic-extractor \                      │       │
│   │   --concurrent-fragments {N} \                     │       │
│   │   --downloader aria2c \                            │       │
│   │   --downloader-args 'aria2c:"--disable-ipv6"' \    │       │
│   │   -o "lecture.%(ext)s" \                           │       │
│   │   {m3u8_url}                                       │       │
│   └────────────────────────────────────────────────────┘       │
│                                                                  │
│   Process:                                                       │
│   1. yt-dlp parses M3U8 playlist                                 │
│   2. Extracts segment URLs                                       │
│   3. aria2c downloads segments concurrently                      │
│   4. yt-dlp merges segments into MP4                             │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4B: Direct Video Download (via aria2c)                     │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   aria2c Command:                                                │
│   ┌────────────────────────────────────────────────────┐       │
│   │ aria2c \                                           │       │
│   │   --disable-ipv6 \                                 │       │
│   │   --out "lecture.mp4" \                            │       │
│   │   {direct_video_url}                               │       │
│   └────────────────────────────────────────────────────┘       │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Optional H.265 Encoding                                 │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   IF --use-h265 specified:                                       │
│                                                                  │
│   ┌────────────────────────────────────────────────────┐       │
│   │ ffmpeg \                                           │       │
│   │   -i lecture.mp4 \                                 │       │
│   │   -c:v libx265 (or hevc_nvenc) \                   │       │
│   │   -c:a copy \                                      │       │
│   │   -crf {value} \                                   │       │
│   │   -preset {preset} \                               │       │
│   │   lecture_h265.mp4                                 │       │
│   └────────────────────────────────────────────────────┘       │
│                                                                  │
│   • Hardware encoding: --use-nvenc (NVIDIA GPU)                 │
│   • Software encoding: libx265 (CPU)                            │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Final File                                              │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   Output:                                                        │
│   out_dir/                                                       │
│   └── Course Name/                                              │
│       └── 01 - Chapter Name/                                    │
│           └── 001 Lecture Title.mp4  ✅                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## DRM Video Download Flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      DRM VIDEO DOWNLOAD                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Extract Media Sources                                   │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   From lecture.asset.media_sources:                             │
│   • Extract DASH manifest URL (MPD file)                        │
│   • Get video format ID                                          │
│   • Get audio format ID                                          │
│                                                                  │
│   Example:                                                       │
│   ┌────────────────────────────────────────────┐               │
│   │ media_sources: [                            │               │
│   │   {                                         │               │
│   │     "download_url": "https://.../manifest.mpd",│            │
│   │     "format_id": "video-1234",              │               │
│   │     "height": 1080                          │               │
│   │   }                                         │               │
│   │ ]                                           │               │
│   └────────────────────────────────────────────┘               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Download Encrypted Segments                             │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   yt-dlp Command (Video Track):                                  │
│   ┌────────────────────────────────────────────────────┐       │
│   │ yt-dlp \                                           │       │
│   │   --enable-file-urls \                            │       │
│   │   --force-generic-extractor \                      │       │
│   │   --allow-unplayable-formats \                     │       │
│   │   --concurrent-fragments {N} \                     │       │
│   │   --downloader aria2c \                            │       │
│   │   -f "video-1234" \                                │       │
│   │   -o "{lecture_id}.encrypted.%(ext)s" \            │       │
│   │   {mpd_url}                                        │       │
│   └────────────────────────────────────────────────────┘       │
│                                                                  │
│   yt-dlp Command (Audio Track):                                  │
│   ┌────────────────────────────────────────────────────┐       │
│   │ yt-dlp \                                           │       │
│   │   ... (same as above) ... \                        │       │
│   │   -f "audio-5678" \                                │       │
│   │   -o "{lecture_id}.encrypted.%(ext)s" \            │       │
│   │   {mpd_url}                                        │       │
│   └────────────────────────────────────────────────────┘       │
│                                                                  │
│   Output Files:                                                  │
│   • {lecture_id}.encrypted.mp4  (video)                         │
│   • {lecture_id}.encrypted.m4a  (audio)                         │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Extract KID (Key ID) from Encrypted Files              │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   Process:                                                       │
│   ┌────────────────────────────────────────────┐               │
│   │ 1. Parse MP4 box structure                  │               │
│   │ 2. Find 'pssh' box (Protection System      │               │
│   │    Specific Header)                         │               │
│   │ 3. Extract Widevine PSSH data               │               │
│   │ 4. Extract Content ID (KID)                 │               │
│   └────────────────────────────────────────────┘               │
│                                                                  │
│   Function: extract_kid(filepath)                                │
│                                                                  │
│   Example Output:                                                │
│   • Video KID: abc123def456...                                   │
│   • Audio KID: xyz789ghi012...                                   │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Lookup Decryption Keys                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   Check keyfile.json:                                            │
│   ┌────────────────────────────────────────────┐               │
│   │ {                                          │               │
│   │   "abc123def456...": "decryption_key_1",   │               │
│   │   "xyz789ghi012...": "decryption_key_2"   │               │
│   │ }                                          │               │
│   └────────────────────────────────────────────┘               │
│                                                                  │
│   IF key found:                                                  │
│     ┌─────────────────────────────┐                            │
│     │ Retrieve decryption key     │                            │
│     │ Continue to decryption      │                            │
│     └─────────────────────────────┘                            │
│                                                                  │
│   IF key NOT found:                                              │
│     ┌─────────────────────────────┐                            │
│     │ ERROR: Key not found        │                            │
│     │ Log error and skip lecture  │                            │
│     └─────────────────────────────┘                            │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Decrypt and Mux (Single Pass)                           │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   ffmpeg Command:                                                │
│   ┌────────────────────────────────────────────────────┐       │
│   │ ffmpeg \                                           │       │
│   │   -decryption_key {video_key} \                    │       │
│   │   -i video.encrypted.mp4 \                          │       │
│   │   -decryption_key {audio_key} \                    │       │
│   │   -i audio.encrypted.m4a \                         │       │
│   │   -c:v copy \                                      │       │
│   │   -c:a copy \                                      │       │
│   │   -f mp4 \                                         │       │
│   │   lecture.mp4                                      │       │
│   └────────────────────────────────────────────────────┘       │
│                                                                  │
│   Process:                                                       │
│   1. Decrypt video track with video_key                          │
│   2. Decrypt audio track with audio_key                          │
│   3. Mux (combine) video + audio                                 │
│   4. Output final MP4 file                                       │
│                                                                  │
│   Optional: H.265 encoding can be applied here                  │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Cleanup Temporary Files                                 │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   Delete:                                                        │
│   • {lecture_id}.encrypted.mp4                                  │
│   • {lecture_id}.encrypted.m4a                                  │
│                                                                  │
│   Keep:                                                          │
│   • {lecture_id}.mp4  (final decrypted video)                    │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Final File                                              │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│   Output:                                                        │
│   out_dir/                                                       │
│   └── Course Name/                                              │
│       └── 01 - Chapter Name/                                    │
│           └── 001 Lecture Title.mp4  ✅                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Flow

### Lecture Processing Entry Point

```
parse_new()
    │
    ├─► For each chapter
    │       │
    │       ├─► Create chapter directory
    │       │
    │       └─► For each lecture
    │               │
    │               ├─► Check if already downloaded
    │               │       │
    │               │       ├─► YES → Skip
    │               │       │
    │               │       └─► NO → Continue
    │               │
    │               ├─► Parse lecture data
    │               │   └─► udemy._parse_lecture(lecture)
    │               │
    │               └─► process_lecture()
    │                       │
    │                       ├─► Check is_encrypted
    │                       │       │
    │                       │       ├─► TRUE → handle_segments() (DRM)
    │                       │       │
    │                       │       └─► FALSE → Direct download
    │                       │
    │                       └─► Download captions (if --download-captions)
    │                       └─► Download assets (if --download-assets)
```

---

## Source Type Decision Tree

```
                    Lecture Source
                         │
                         ▼
            ┌────────────────────────┐
            │  Check source.type     │
            └────────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐      ┌────────┐      ┌────────┐
    │  "hls" │      │ "video"│      │ "dash" │
    └───┬────┘      └───┬────┘      └───┬────┘
        │               │                │
        │               │                │
        ▼               ▼                ▼
   ┌─────────┐     ┌─────────┐     ┌─────────┐
   │ yt-dlp  │     │ aria2c  │     │ yt-dlp  │
   │ +       │     │ direct  │     │ (DRM)   │
   │ aria2c  │     │ download│     │         │
   └─────────┘     └─────────┘     └─────────┘
```

---

## Download Tools Used

### 1. yt-dlp

**Purpose:** Download streaming video formats (HLS, DASH)

**Key Features:**
- Parses M3U8 playlists (HLS)
- Parses MPD manifests (DASH)
- Handles encrypted segments
- Concurrent fragment downloads
- Automatic segment merging

**Usage:**
```bash
yt-dlp \
  --enable-file-urls \
  --force-generic-extractor \
  --concurrent-fragments 10 \
  --downloader aria2c \
  -o "output.%(ext)s" \
  {url}
```

### 2. aria2c

**Purpose:** Fast multi-connection downloader

**Key Features:**
- Concurrent connections
- Resume interrupted downloads
- Fast segment downloading
- Used by yt-dlp for HLS/DASH

**Usage:**
```bash
aria2c \
  --disable-ipv6 \
  --out "output.mp4" \
  {direct_url}
```

### 3. ffmpeg

**Purpose:** Video processing, decryption, muxing, encoding

**Key Features:**
- DRM decryption (with keys)
- Video/audio muxing
- H.265 encoding
- Hardware acceleration (NVIDIA)

**Usage (Decryption):**
```bash
ffmpeg \
  -decryption_key {key} \
  -i encrypted.mp4 \
  -c copy \
  output.mp4
```

**Usage (Encoding):**
```bash
ffmpeg \
  -i input.mp4 \
  -c:v libx265 \
  -c:a copy \
  -crf 28 \
  output.mp4
```

---

## File Structure During Download

### Non-DRM Download

```
chapter_dir/
├── 001 Lecture Title.mp4.tmp    (downloading)
└── 001 Lecture Title.mp4        (final, after completion)
```

### DRM Download

```
chapter_dir/
├── 12345.encrypted.mp4          (encrypted video, temporary)
├── 12345.encrypted.m4a          (encrypted audio, temporary)
├── 12345.mp4                    (decrypting/muxing)
└── 001 Lecture Title.mp4        (final, after cleanup)
```

---

## Quality Selection Logic

```
Available Qualities: [1080p, 720p, 480p, 360p, 144p]

IF --quality specified:
    ┌─────────────────────────────────────┐
    │ Find closest match                  │
    │ Example: -q 720                     │
    │   → Selects 720p                    │
    │ Example: -q 900                      │
    │   → Selects 1080p (closest above)   │
    └─────────────────────────────────────┘

ELSE:
    ┌─────────────────────────────────────┐
    │ Select highest quality              │
    │ → Selects 1080p                    │
    └─────────────────────────────────────┘
```

---

## Concurrent Downloads

### HLS/DASH Segments

```
Concurrent Fragments: --concurrent-downloads (default: 10, max: 30)

┌─────────────────────────────────────────┐
│  Segment 1  ──┐                         │
│  Segment 2  ──┤                         │
│  Segment 3  ──┤                         │
│  Segment 4  ──┼──► aria2c ──► Merge    │
│  Segment 5  ──┤                         │
│  ...         ──┤                         │
│  Segment N  ──┘                         │
└─────────────────────────────────────────┘
```

### Multiple Lectures

```
Lectures download sequentially (one at a time):

Lecture 1 ──► Download ──► Complete ──►
                                        │
Lecture 2 ─────────────────────────────┘
           ──► Download ──► Complete ──►
                                        │
Lecture 3 ─────────────────────────────┘
           ──► Download ──► Complete
```

---

## Error Handling

```
┌─────────────────────────────────────────┐
│         Download Attempt                 │
└──────────────┬──────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Check Return Code   │
    └──────┬───────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│  = 0   │   │  ≠ 0   │
│ (OK)   │   │(ERROR) │
└───┬────┘   └───┬────┘
    │            │
    │            ▼
    │    ┌───────────────┐
    │    │ Log Warning   │
    │    │ Skip Lecture  │
    │    └───────────────┘
    │
    ▼
┌───────────────┐
│ Continue Next │
│   Lecture     │
└───────────────┘
```

---

## Code References

### Key Functions

- `parse_new()`: Main download orchestrator
- `process_lecture()`: Processes individual lecture
- `handle_segments()`: Handles DRM video download
- `download_aria()`: Direct video download via aria2c
- `mux_process()`: Decrypts and muxes DRM video/audio
- `extract_kid()`: Extracts KID from encrypted files

### Key Files

- `main.py`: Download logic (lines 1547-1646, 1296-1403)
- `utils.py`: KID extraction utilities
- `keyfile.json`: Decryption keys (user-provided)

---

## Performance Optimization

### 1. Concurrent Fragment Downloads

```bash
--concurrent-downloads 20  # Download 20 segments simultaneously
```

**Impact:**
- Faster HLS/DASH downloads
- Better bandwidth utilization
- Max: 30 concurrent fragments

### 2. Skip HLS Parsing

```bash
--skip-hls  # Skip HLS streams (faster, but may miss 1080p)
```

**Trade-off:**
- ✅ Faster course info fetching
- ❌ May miss 1080p quality (HLS often has best quality)

### 3. Caching

```bash
--save-to-file   # Cache course data
--load-from-file # Load from cache (skip API calls)
```

**Impact:**
- Faster repeated runs
- Note: Asset URLs expire after time

---

## Summary

### Non-DRM Videos
1. Extract sources → 2. Select quality → 3. Download (yt-dlp/aria2c) → 4. Optional encoding → 5. Done

### DRM Videos
1. Extract media sources → 2. Download encrypted segments → 3. Extract KID → 4. Lookup keys → 5. Decrypt & mux → 6. Cleanup → 7. Done

Both paths result in a final MP4 file ready for viewing!
