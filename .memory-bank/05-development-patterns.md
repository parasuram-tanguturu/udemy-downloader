# Development Patterns & Conventions

## Code Style

### Global Variables

The codebase uses many global variables for configuration:

- `bearer_token`, `course_url`, `quality`, `dl_assets`, etc.
- Set in `pre_run()` function
- Used throughout the codebase

### Error Handling

- **Connection Errors**: Retry with sleep (0.8s)
- **Download Errors**: Log and skip, continue with next item
- **Key Errors**: Log error and return early
- **Subprocess Errors**: Check return codes, log failures

### Logging

- Use `logger` object (configured in `pre_run()`)
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Format: `[timestamp] [logger] [function:line] LEVEL: message`
- Both console (colored) and file output

### File Naming

- Use `sanitize_filename()` from `pathvalidate` for all filenames
- Remove emojis with `deEmojify()` function
- Lecture numbering: `{counter:03d} Title.ext`
- Chapter numbering: `{index:02d} - Title`

## API Interaction Patterns

### Session Management

```python
session = Session()
session.visit(portal_name)  # Get Cloudflare cookies
session._get(url)  # Make authenticated request
```

### Pagination

```python
def _handle_pagination(url, params=None):
    # Fetch first page
    data = session._get(url, params).json()
    # Follow 'next' links until done
    while data.get("next"):
        # Fetch next page and merge results
```

### Retry Logic

```python
for i in range(10):
    req = session._get(url)
    if req.ok or req.status_code in [502, 503]:
        return req
    time.sleep(0.8)
```

## Download Patterns

### Direct Downloads

```python
download_aria(url, directory, filename)
# Uses aria2c with optimized settings
```

### Stream Downloads (HLS/DASH)

```python
# Use yt-dlp with aria2c downloader
subprocess.Popen([
    "yt-dlp",
    "--downloader", "aria2c",
    "--concurrent-fragments", str(concurrent_downloads),
    ...
])
```

### DRM Decryption

```python
# 1. Download encrypted segments
# 2. Extract KID from MP4
video_kid = extract_kid(video_file)
# 3. Lookup key
video_key = keys[video_kid]
# 4. Decrypt and mux with ffmpeg
ffmpeg -decryption_key {key} -i video -i audio ...
```

## Data Structures

### Course Object

```python
{
    "course_id": int,
    "title": str,
    "course_title": str,
    "chapters": [
        {
            "chapter_title": str,
            "chapter_index": int,
            "lectures": [
                {
                    "index": int,
                    "lecture_title": str,
                    "sources": [...],  # For unencrypted
                    "video_sources": [...],  # For encrypted
                    "subtitles": [...],
                    "assets": [...],
                    "is_encrypted": bool
                }
            ]
        }
    ]
}
```

### Source Object (Unencrypted)

```python
{
    "type": "video" | "hls",
    "height": str,
    "width": str,
    "extension": str,
    "download_url": str
}
```

### Source Object (Encrypted/DASH)

```python
{
    "type": "dash",
    "height": str,
    "width": str,
    "format_id": str,  # "video_format,audio_format"
    "extension": str,
    "download_url": str,  # MPD file URI
    "tbr": int  # Bitrate
}
```

## Subprocess Patterns

### FFmpeg Commands

- Windows: Direct command string
- Linux/Mac: Prefixed with `nice -n 7` for lower priority
- Use shell=True for command execution
- Log stdout/stderr via `log_subprocess_output()`

### yt-dlp Integration

- Always use `--enable-file-urls` for local MPD/M3U8 files
- Use `--force-generic-extractor` for DASH streams
- Use `--allow-unplayable-formats` for encrypted content
- Use `--concurrent-fragments` for parallel segment downloads

## File Path Patterns

### Path Construction

```python
# Base directories
DOWNLOAD_DIR = os.path.join(os.getcwd(), "out_dir")
SAVED_DIR = os.path.join(os.getcwd(), "saved")
LOG_DIR_PATH = os.path.join(os.getcwd(), "logs")

# Course structure
course_dir = os.path.join(DOWNLOAD_DIR, course_name)
chapter_dir = os.path.join(course_dir, chapter_title)
lecture_path = os.path.join(chapter_dir, lecture_filename)
```

### Temporary Files

- M3U8/MPD files: `temp/index_{asset_id}.m3u8`
- Encrypted segments: `{lecture_id}.encrypted.mp4`
- Cleaned up after processing

## Template Rendering

### HTML Templates

1. Load template file
2. Replace placeholders:
   - `__data_placeholder__`: JSON data
   - `__title_placeholder__`: Title text
3. Write to lecture directory

## Quality Selection Logic

```python
# Sort by height (descending)
sources = sorted(sources, key=lambda x: int(x.get("height")), reverse=True)

# If quality specified, find closest match
if isinstance(quality, int):
    source = min(sources, key=lambda x: abs(int(x.get("height")) - quality))
else:
    source = sources[0]  # Best quality
```

## Chapter Filtering Logic

```python
# Parse filter string "1,3-5,7"
chapters = set()
for part in chapter_str.split(","):
    if "-" in part:
        start, end = part.split("-")
        chapters.update(range(int(start), int(end) + 1))
    else:
        chapters.add(int(part))

# Skip chapters not in filter
if chapter_filter and current_chapter_index not in chapter_filter:
    continue
```

## Common Patterns to Follow

1. **Always sanitize filenames** before writing to disk
2. **Check file existence** before downloading (skip if exists)
3. **Use path.join()** instead of string concatenation
4. **Log important operations** with appropriate levels
5. **Handle exceptions** gracefully, log and continue
6. **Clean up temp files** after processing
7. **Use subprocess for external tools** (ffmpeg, aria2c, yt-dlp)
8. **Return early** on errors rather than nested conditionals
