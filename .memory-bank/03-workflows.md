# Key Workflows

## Interactive Workflow

The `interactive_udemy.py` wrapper provides a user-friendly menu-driven interface:

1. **Main Action Selection**
   - Generate curriculum only (default)
   - Download course
   - View course info only

2. **Authentication Selection**
   - Bearer token (with instructions for getting from browser cookies)
   - Browser cookies (automatic extraction)
   - Skip (use .env file)

3. **Download Options** (if downloading)
   - Lectures, captions, assets, quizzes
   - Quality, language, output directory
   - Advanced options (H.265, chapter filtering, etc.)

4. **Execution & Output**
   - Executes `main.py` with constructed arguments
   - Displays output directory path
   - Optionally opens directory in Finder (macOS)

**Usage**: Run `python3 interactive_udemy.py` or use the `udemy` alias if configured.

## Authentication Flow

> **📖 For detailed authentication documentation, see [07-authentication.md](./07-authentication.md)**

1. **Bearer Token or Cookies**
   - Bearer token can be provided via:
     - Command-line argument (`-b` or `--bearer`)
     - Environment variable (`UDEMY_BEARER` in `.env`)
     - Interactive prompt (in interactive mode)
   - **Note**: Bearer token = `access_token` cookie value from browser
     - Get it from Developer Tools > Application > Cookies > `access_token`
   - Cookies can be extracted from browser using `--browser` flag
   - Supported browsers: chrome, firefox, opera, edge, brave, chromium, vivaldi, safari
   - Cookie file support (Netscape format)

2. **Session Initialization**
   - Create `Session` object with custom SSL adapter
   - Make visit request to get Cloudflare cookies
   - Set authentication headers if bearer token provided

## Course Discovery Flow

1. **URL Parsing**
   - Extract portal name (e.g., "www") from course URL
   - Extract course name/slug from URL

2. **Course Lookup**
   - Fetch user's subscribed courses from API
   - Also check subscription course enrollments
   - Match by `published_title` or course ID
   - Fallback to archived courses if not found

3. **Course ID Extraction**
   - Get course ID from matched course object
   - Use course ID for subsequent API calls

## Curriculum Fetching Flow

1. **API Request**
   - Call curriculum items endpoint with pagination
   - Request specific fields for lectures, quizzes, chapters, assets

2. **Pagination Handling**
   - `_handle_pagination()` method processes all pages
   - Combines results from multiple pages
   - Handles rate limiting and retries

3. **Data Structure**
   - Organize curriculum into chapters
   - Each chapter contains lectures and quizzes
   - Lectures contain asset data with sources

## Lecture Processing Flow

### Unencrypted Lectures

1. **Source Extraction**
   - Extract `stream_urls.Video` sources
   - Parse HLS playlists if present (unless `--skip-hls`)
   - Sort sources by quality (height)

2. **Quality Selection**
   - If `--quality` specified, find closest match
   - Otherwise, select highest quality

3. **Download**
   - **HLS streams**: Use yt-dlp with aria2c downloader
   - **Direct streams**: Use aria2c directly
   - Optional H.265 re-encoding if `--use-h265` specified

### Encrypted (DRM) Lectures

1. **Media Source Extraction**
   - Extract `media_sources` (DASH streams)
   - Parse MPD file using yt-dlp
   - Extract video and audio format IDs

2. **Segment Download**
   - Use yt-dlp to download encrypted segments
   - Downloads both video and audio tracks
   - Saves as `.encrypted.mp4` and `.encrypted.m4a`

3. **KID Extraction**
   - Parse MP4 boxes to find PSSH header
   - Extract Widevine PSSH data
   - Get content ID (KID) for both video and audio

4. **Key Lookup**
   - Lookup KID in `keyfile.json`
   - Retrieve corresponding decryption key

5. **Decryption & Muxing**
   - Use ffmpeg with `-decryption_key` flag
   - Decrypt and mux video/audio in single pass
   - Optional H.265 encoding if specified
   - Clean up temporary encrypted files

## Caption Processing Flow

1. **Extraction**
   - Extract caption tracks from lecture asset
   - Filter by language if `--lang` specified
   - Support for "all" languages

2. **Download**
   - Download VTT or SRT file using aria2c
   - Save with language code in filename

3. **Conversion**
   - If VTT format, convert to SRT using `vtt_to_srt.py`
   - Delete VTT file unless `--keep-vtt` specified

## Asset Processing Flow

1. **Asset Types**
   - **Files**: Direct download
   - **Source Code**: Download from source code URLs
   - **Presentations**: Download PPT/PDF files
   - **E-Books**: Download ebook files
   - **Audio**: Download audio files
   - **Articles**: Generate HTML from body content
   - **External Links**: Create `.url` files and append to `external-links.txt`

2. **Naming**
   - Assets prefixed with lecture number (e.g., "001 filename.pdf")
   - Filenames sanitized for filesystem compatibility

## Quiz Processing Flow

1. **Quiz Detection**
   - Identify quiz lectures by `_class == "quiz"`
   - Fetch quiz data from API

2. **Quiz Types**
   - **Normal Quiz**: Multiple choice, true/false, etc.
     - Generate HTML using `quiz_template.html`
   - **Coding Assignment**: Coding problems
     - Generate HTML using `coding_assignment_template.html`
     - Includes instructions, tests, and solutions

3. **Template Rendering**
   - Load HTML template
   - Inject quiz data as JSON
   - Save to lecture directory

## Chapter Filtering Flow

1. **Filter Parsing**
   - Parse `--chapter` argument (e.g., "1,3-5,7")
   - Convert to set of chapter indices

2. **Filtering**
   - Skip chapters not in filter during processing
   - Applies to both download and info modes

## Caching Flow

1. **Save to File** (`--save-to-file`)
   - Save raw curriculum JSON to `saved/course_content.json`
   - Save parsed course structure to `saved/_udemy.json`
   - Note: Asset URLs expire, so cache has limited lifetime

2. **Load from File** (`--load-from-file`)
   - Load curriculum from cached JSON
   - Skip API calls for course data
   - Faster for repeated runs

## Curriculum Markdown Generation Flow

### Fast Mode (`--curriculum-only`)

Use `--curriculum-only` flag for fast curriculum generation without detailed lecture parsing:

```bash
python main.py -c <Course URL> -b <token> --curriculum-only
```

### Detailed Mode (with `--info` or during download)

1. **Generation Trigger**
   - Automatically generated during course processing
   - Called in `parse_new()` after course directory creation
   - Also generated in `_print_course_info()` for info-only mode

2. **Data Collection**
   - Processes all chapters and lectures
   - Respects chapter filtering if `--chapter` is specified

3. **Content Generation**
   - Course header with title and statistics
   - For each chapter: chapter title with lecture list
   - For each lecture: simple checkbox format
   - Special handling for quizzes (marked with *(Quiz)*)

4. **File Output**
   - Saved as `curriculum.md` in course directory
   - UTF-8 encoded markdown format
   - Error handling prevents failures from blocking downloads
