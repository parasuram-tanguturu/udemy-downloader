# Caption/Subtitle Download Flow

This document explains how captions/subtitles are downloaded from Udemy courses with detailed visual flow diagrams.

## Overview

The caption download feature allows users to download subtitle files (VTT or SRT format) for course lectures. Captions are automatically converted from VTT to SRT format for better compatibility, with an option to keep the original VTT files.

---

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START: --download-captions              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Parse Lecture Data                                   │
│ ─────────────────────────────────────────────────────────── │
│ • Fetch lecture information from API                         │
│ • Extract asset data                                          │
│ • Parse captions from asset.captions                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Extract Subtitle Information                         │
│ ─────────────────────────────────────────────────────────── │
│ • Filter caption tracks                                      │
│ • Extract language, URL, format                               │
│ • Build subtitle objects                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Filter by Language                                   │
│ ─────────────────────────────────────────────────────────── │
│ • Check --lang flag (default: "en")                          │
│ • Filter: lang == caption_locale OR "all"                   │
│ • Process matching subtitles                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Download Caption File                                │
│ ─────────────────────────────────────────────────────────── │
│ • Generate filename                                           │
│ • Check if already exists                                    │
│ • Download via aria2c                                         │
│ • Retry on failure (up to 3 times)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Convert VTT to SRT (if needed)                      │
│ ─────────────────────────────────────────────────────────── │
│ • Check if extension is "vtt"                                │
│ • Parse WebVTT format                                        │
│ • Convert to SRT format                                      │
│ • Write SRT file                                             │
│ • Delete VTT (unless --keep-vtt)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT: Caption Files                      │
│         {lecture_title}_{language}.srt                       │
│         {lecture_title}_{language}.vtt (if --keep-vtt)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Extraction Flow

### Step 1: Subtitle Extraction from Asset Data

```
┌─────────────────────────────────────────────────────────────┐
│              SUBTITLE EXTRACTION FLOW                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1.1: Input Data Structure (asset.captions)                   │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ asset = {                                  │           │
│   │   "id": 123456,                            │           │
│   │   "captions": [                            │           │
│   │     {                                      │           │
│   │       "_class": "caption",                │           │
│   │       "url": "https://.../en.vtt",        │           │
│   │       "language": "en",                    │           │
│   │       "srclang": "en",                    │           │
│   │       "label": "English",                  │           │
│   │       "locale_id": "en_US"                │           │
│   │     },                                     │           │
│   │     {                                      │           │
│   │       "_class": "caption",                │           │
│   │       "url": "https://.../es.srt",        │           │
│   │       "language": "es",                   │           │
│   │       "srclang": "es",                    │           │
│   │       "label": "Spanish",                 │           │
│   │       "locale_id": "es_ES"                │           │
│   │     }                                      │           │
│   │   ]                                        │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1.2: _extract_subtitles(tracks) Function                     │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   FOR each track in tracks:                                  │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 1. Validate Track                           │           │
│   │    IF not isinstance(track, dict):          │           │
│   │      SKIP                                   │           │
│   │    IF track.get("_class") != "caption":     │           │
│   │      SKIP                                   │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 2. Extract Download URL                     │           │
│   │    download_url = track.get("url")          │           │
│   │    IF not download_url or not string:      │           │
│   │      SKIP                                   │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 3. Extract Language                          │           │
│   │    lang = (                                 │           │
│   │      track.get("language")                 │           │
│   │      OR track.get("srclang")                │           │
│   │      OR track.get("label")                  │           │
│   │      OR track["locale_id"].split("_")[0]    │           │
│   │    )                                         │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 4. Detect Format                             │           │
│   │    ext = "vtt" if "vtt" in URL else "srt"  │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 5. Build Subtitle Object                    │           │
│   │    subtitle = {                            │           │
│   │      "type": "subtitle",                    │           │
│   │      "language": lang,                     │           │
│   │      "extension": ext,                      │           │
│   │      "download_url": download_url           │           │
│   │    }                                         │           │
│   │    _temp.append(subtitle)                   │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ✅ Subtitles Extracted
```

---

## Complete Download Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER: --download-captions             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Parse Lecture                   │
        │  _parse_lecture()                 │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Extract Asset Data              │
        │  asset.get("captions")           │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Extract Subtitles                 │
        │  _extract_subtitles(tracks)       │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Add to parsed_lecture            │
        │  parsed_lecture["subtitles"] = [] │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Check Download Flag              │
        │  IF dl_captions AND              │
        │     subtitles != None AND         │
        │     lecture_extension == None:    │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │   YES        │    │     NO       │
    │              │    │              │
    │ Process      │    │ Skip         │
    │ Captions     │    │ Captions     │
    └──────┬───────┘    └──────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │  FOR each subtitle:              │
    │    lang = subtitle.get("language")│
    │    IF lang == caption_locale OR   │
    │       caption_locale == "all":   │
    └──────────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────┐
        │  process_caption()                │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Generate Filename                │
        │  {lecture_title}_{lang}.{ext}     │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Check if Exists                  │
        │  IF file exists:                  │
        │    Log "already downloaded"       │
        │    SKIP                           │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Download via aria2c              │
        │  download_aria(url, dir, filename)│
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  Success     │    │   Error      │
    │              │    │              │
    │ Continue     │    │ Retry (max 3)│
    └──────┬───────┘    └──────┬───────┘
           │                    │
           │                    │
           ▼                    ▼
    ┌──────────────────────────────────┐
    │  Check Format                     │
    │  IF extension == "vtt":          │
    └──────────────┬───────────────────┘
                   │
            ┌──────┴──────┐
            │             │
            ▼             ▼
    ┌──────────────┐  ┌──────────────┐
    │   YES        │  │     NO        │
    │              │  │               │
    │ Convert      │  │ Done          │
    │ VTT→SRT      │  │               │
    └──────┬───────┘  └───────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │  Convert VTT to SRT               │
    │  convert(directory, filename)      │
    └──────────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────┐
        │  Check --keep-vtt                │
        │  IF not keep_vtt:                │
        │    Delete VTT file               │
        └──────────────┬───────────────────┘
                       │
                       ▼
                ✅ Caption Downloaded
```

---

## Language Filtering Flow

```
┌─────────────────────────────────────────────────────────────┐
│              LANGUAGE FILTERING LOGIC                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Get caption_locale               │
        │  (Default: "en", or --lang flag)  │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  "all"       │    │  Specific    │
    │              │    │  Language    │
    │ Download     │    │  (e.g., "en") │
    │ All          │    │              │
    └──────┬───────┘    └──────┬───────┘
           │                    │
           │                    │
           ▼                    ▼
    ┌──────────────────────────────────┐
    │  FOR each subtitle:              │
    │    lang = subtitle.get("language")│
    │    IF caption_locale == "all":    │
    │      PROCESS (download all)       │
    │    ELIF lang == caption_locale:   │
    │      PROCESS (download matching)  │
    │    ELSE:                          │
    │      SKIP (filter out)            │
    └──────────────────────────────────┘
```

**Examples:**
- `--lang en` → Downloads only English captions
- `--lang es` → Downloads only Spanish captions
- `--lang all` → Downloads all available languages

---

## Caption Processing Flow

### process_caption() Function

```
┌─────────────────────────────────────────────────────────────┐
│              process_caption() FLOW                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Generate Filename                                    │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   filename = f"{lecture_title}_{language}.{extension}"       │
│                                                              │
│   Example:                                                   │
│   "001 About this Course_en.vtt"                            │
│                                                              │
│   filename_no_ext = f"{lecture_title}_{language}"           │
│                                                              │
│   Example:                                                   │
│   "001 About this Course_en"                                │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Check if File Exists                                 │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   filepath = os.path.join(lecture_dir, filename)            │
│                                                              │
│   IF os.path.isfile(filepath):                              │
│     Log: "Caption already downloaded"                        │
│     RETURN (skip download)                                    │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Download Caption File                                 │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Log: "Downloading caption: {filename}"                     │
│                                                              │
│   TRY:                                                       │
│     ret_code = download_aria(                               │
│       caption.get("download_url"),                          │
│       lecture_dir,                                           │
│       filename                                               │
│     )                                                        │
│                                                              │
│   EXCEPT Exception:                                          │
│     IF tries >= 3:                                          │
│       Log error, skip                                        │
│     ELSE:                                                    │
│       Retry (recursive call with tries + 1)                  │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Convert VTT to SRT (if needed)                       │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   IF caption.get("extension") == "vtt":                     │
│                                                              │
│     TRY:                                                     │
│       Log: "Converting caption to SRT format..."            │
│       convert(lecture_dir, filename_no_ext)                  │
│       Log: "Caption conversion complete."                     │
│                                                              │
│       IF not keep_vtt:                                       │
│         os.remove(filepath)  # Delete VTT file               │
│                                                              │
│     EXCEPT Exception:                                        │
│       Log exception (conversion failed)                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## VTT to SRT Conversion Flow

```
┌─────────────────────────────────────────────────────────────┐
│              VTT TO SRT CONVERSION                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Open Files                                            │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   vtt_filepath = os.path.join(                               │
│     directory,                                               │
│     filename + ".vtt"                                        │
│   )                                                          │
│                                                              │
│   srt_filepath = os.path.join(                               │
│     directory,                                                 │
│     filename + ".srt"                                        │
│   )                                                          │
│                                                              │
│   srt = open(srt_filepath, "w", encoding="utf8")            │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Parse WebVTT Format                                   │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   FOR each caption in WebVTT().read(vtt_filepath):          │
│                                                              │
│     index += 1                                               │
│                                                              │
│     start = SubRipTime(                                       │
│       0, 0,                                                  │
│       caption.start_in_seconds                               │
│     )                                                        │
│                                                              │
│     end = SubRipTime(                                        │
│       0, 0,                                                  │
│       caption.end_in_seconds                                 │
│     )                                                        │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Write SRT Format                                      │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   text = html.unescape(caption.text)                         │
│                                                              │
│   srt_item = SubRipItem(                                      │
│     index,                                                   │
│     start,                                                   │
│     end,                                                     │
│     text                                                     │
│   )                                                          │
│                                                              │
│   srt.write(str(srt_item) + "\n")                            │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ✅ SRT File Created
```

---

## Data Structure Flow

### Input: Asset Captions Structure

```
asset
├── id: 123456
├── asset_type: "Video"
└── captions: [
      {
        _class: "caption",
        url: "https://udemy.com/captions/en.vtt",
        language: "en",
        srclang: "en",
        label: "English",
        locale_id: "en_US"
      },
      {
        _class: "caption",
        url: "https://udemy.com/captions/es.srt",
        language: "es",
        srclang: "es",
        label: "Spanish",
        locale_id: "es_ES"
      },
      {
        _class: "caption",
        url: "https://udemy.com/captions/fr.vtt",
        language: "fr",
        srclang: "fr",
        label: "French",
        locale_id: "fr_FR"
      }
    ]
```

### Output: Subtitle Objects

```
subtitles = [
  {
    type: "subtitle",
    language: "en",
    extension: "vtt",
    download_url: "https://udemy.com/captions/en.vtt"
  },
  {
    type: "subtitle",
    language: "es",
    extension: "srt",
    download_url: "https://udemy.com/captions/es.srt"
  },
  {
    type: "subtitle",
    language: "fr",
    extension: "vtt",
    download_url: "https://udemy.com/captions/fr.vtt"
  }
]
```

### Output: Files on Disk

```
out_dir/
└── course-name/
    └── Chapter 01/
        ├── 001 About this Course_en.srt  ← Converted from VTT
        ├── 001 About this Course_es.srt  ← Already SRT
        └── 001 About this Course_fr.srt  ← Converted from VTT
```

---

## Error Handling and Retry Logic

```
┌─────────────────────────────────────────────────────────────┐
│              ERROR HANDLING FLOW                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  download_aria()                  │
        │  (Download attempt)               │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  Success     │    │   Error      │
    │              │    │              │
    │  Continue    │    │  Exception  │
    └──────────────┘    └──────┬───────┘
                               │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌──────────────┐    ┌──────────────┐
            │ tries >= 3    │    │ tries < 3     │
            │               │    │               │
            │ Log error     │    │ Log retry     │
            │ Skip caption  │    │ Recursive call│
            │               │    │ process_caption│
            │               │    │ (tries + 1)   │
            └──────────────┘    └───────────────┘
```

**Retry Strategy:**
- ✅ Maximum 3 retry attempts
- ✅ Exponential backoff (via aria2c)
- ✅ Logs each attempt
- ✅ Skips caption if all retries fail

---

## Conversion Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│              CONVERSION ERROR HANDLING                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  convert() Function              │
        │  (VTT to SRT conversion)         │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  Success     │    │   Error      │
    │              │    │              │
    │  Delete VTT  │    │  Log Exception│
    │  (if flag)   │    │  Keep VTT    │
    │              │    │  (fallback)  │
    └──────────────┘    └──────────────┘
```

**Error Strategy:**
- ✅ Non-blocking: Errors don't stop downloads
- ✅ Logged: Full exception details logged
- ✅ Fallback: VTT file kept if conversion fails
- ✅ Graceful: Program continues even if conversion fails

---

## File Naming Convention

### Filename Format

```
{lecture_title}_{language}.{extension}
```

**Components:**
- `lecture_title`: Sanitized lecture title (spaces replaced, special chars removed)
- `language`: Language code (e.g., "en", "es", "fr")
- `extension`: File extension ("vtt" or "srt")

### Examples

```
Input:
  lecture_title: "001 About this Course"
  language: "en"
  extension: "vtt"

Output:
  filename: "001 About this Course_en.vtt"
  filename_no_ext: "001 About this Course_en"

After conversion:
  "001 About this Course_en.srt"  (VTT deleted if --keep-vtt not set)
```

---

## Integration with Lecture Processing

```
┌─────────────────────────────────────────────────────────────┐
│              LECTURE PROCESSING INTEGRATION                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  parse_new()                     │
        │  (Main download function)        │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  FOR each chapter:                │
        │    FOR each lecture:              │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  _parse_lecture()                 │
        │  (Extract lecture data)           │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Extract subtitles                │
        │  parsed_lecture["subtitles"]      │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Check dl_captions flag           │
        │  AND subtitles != None            │
        │  AND lecture_extension == None   │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │   YES        │    │     NO       │
    │              │    │              │
    │ Process      │    │ Skip         │
    │ Captions     │    │ Captions    │
    └──────┬───────┘    └──────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │  FOR each subtitle:               │
    │    Filter by language             │
    │    process_caption()              │
    └──────────────────────────────────┘
```

**Note:** Captions are only processed for regular lectures (not articles, quizzes, or coding assignments).

---

## Format Detection Logic

```
┌─────────────────────────────────────────────────────────────┐
│              FORMAT DETECTION                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Get download_url                │
        │  Example:                        │
        │  "https://.../captions/en.vtt"   │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Extract Extension                │
        │  url.rsplit(".", 1)[-1]          │
        │  Result: "vtt"                    │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  "vtt" in    │    │  Not "vtt"   │
    │  extension   │    │              │
    │              │    │              │
    │  ext = "vtt" │    │  ext = "srt" │
    └──────────────┘    └──────────────┘
```

**Logic:**
- If URL ends with ".vtt" → extension = "vtt"
- Otherwise → extension = "srt"

---

## Download Tool: aria2c

```
┌─────────────────────────────────────────────────────────────┐
│              ARIA2C DOWNLOAD PROCESS                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  download_aria() Function         │
        │  ──────────────────────────────── │
        │                                   │
        │  Command:                         │
        │  aria2c [options] <url>            │
        │                                   │
        │  Options:                         │
        │  • --dir={lecture_dir}            │
        │  • --out={filename}               │
        │  • --max-connection-per-server=1   │
        │  • --split=1                      │
        │  • --min-split-size=1M             │
        │  • --max-tries=3                   │
        │  • --retry-wait=2                  │
        │  • --continue                      │
        │  • --log-level=warn                │
        │  • --file-allocation=none           │
        │  • --no-conf                       │
        │  • --allow-overwrite=true          │
        └──────────────────────────────────┘
```

**Features:**
- ✅ Resume capability (--continue)
- ✅ Automatic retries (--max-tries=3)
- ✅ Connection management
- ✅ Progress logging

---

## Complete Code Flow Diagram

```
main()
    │
    ├─► Parse arguments
    │       │
    │       ├─► --download-captions → dl_captions = True
    │       └─► --lang {lang} → caption_locale = {lang}
    │
    ├─► parse_new()
    │       │
    │       └─► FOR each chapter:
    │               │
    │               └─► FOR each lecture:
    │                       │
    │                       ├─► _parse_lecture()
    │                       │       │
    │                       │       ├─► Extract asset data
    │                       │       │
    │                       │       └─► _extract_subtitles()
    │                       │           │
    │                       │           ├─► FOR each track:
    │                       │           │   ├─► Validate _class == "caption"
    │                       │           │   ├─► Extract URL
    │                       │           │   ├─► Extract language
    │                       │           │   ├─► Detect format
    │                       │           │   └─► Build subtitle object
    │                       │           │
    │                       │           └─► Return subtitle list
    │                       │
    │                       └─► IF dl_captions AND subtitles:
    │                               │
    │                               └─► FOR each subtitle:
    │                                       │
    │                                       ├─► Filter by language
    │                                       │
    │                                       └─► process_caption()
    │                                           │
    │                                           ├─► Generate filename
    │                                           │
    │                                           ├─► Check if exists
    │                                           │
    │                                           ├─► download_aria()
    │                                           │   └─► Retry on error
    │                                           │
    │                                           └─► IF VTT:
    │                                                   │
    │                                                   └─► convert()
    │                                                       │
    │                                                       ├─► Parse WebVTT
    │                                                       │
    │                                                       └─► Write SRT
    │                                                           │
    │                                                           └─► Delete VTT (if flag)
```

---

## Usage Examples

### Example 1: Download English Captions (Default)

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  -b {bearer_token} \
  --download-captions
```

**Result:**
- Downloads only English captions
- Converts VTT to SRT
- Deletes VTT files

---

### Example 2: Download Specific Language

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  -b {bearer_token} \
  --download-captions \
  -l es
```

**Result:**
- Downloads only Spanish captions
- Converts VTT to SRT if needed
- Deletes VTT files

---

### Example 3: Download All Languages

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  -b {bearer_token} \
  --download-captions \
  -l all
```

**Result:**
- Downloads all available caption languages
- Converts VTT to SRT
- Deletes VTT files

---

### Example 4: Keep VTT Files

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  -b {bearer_token} \
  --download-captions \
  --keep-vtt
```

**Result:**
- Downloads captions
- Converts VTT to SRT
- **Keeps** VTT files (doesn't delete)

---

### Example 5: Captions Only (Skip Videos)

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  -b {bearer_token} \
  --skip-lectures \
  --download-captions \
  -l all
```

**Result:**
- Skips video downloads
- Downloads all caption languages
- Faster processing

---

## File Output Structure

```
out_dir/
└── {course_name}/
    └── {chapter_name}/
        ├── {lecture_title}_en.srt
        ├── {lecture_title}_es.srt
        ├── {lecture_title}_fr.srt
        └── {lecture_title}_de.srt
```

**With --keep-vtt:**
```
out_dir/
└── {course_name}/
    └── {chapter_name}/
        ├── {lecture_title}_en.vtt  ← Original
        ├── {lecture_title}_en.srt   ← Converted
        ├── {lecture_title}_es.srt
        └── ...
```

---

## Language Code Extraction Priority

```
┌─────────────────────────────────────────────────────────────┐
│              LANGUAGE EXTRACTION PRIORITY                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Try in order:                   │
        │  1. track.get("language")        │
        │  2. track.get("srclang")         │
        │  3. track.get("label")           │
        │  4. track["locale_id"].split("_")[0]│
        └──────────────────────────────────┘
```

**Examples:**
- `{"language": "en"}` → "en"
- `{"srclang": "es"}` → "es"
- `{"label": "French"}` → "French"
- `{"locale_id": "fr_FR"}` → "fr"

---

## Code References

### Key Functions

- `_extract_subtitles()`: Extract subtitle data from tracks (lines 687-713)
- `process_caption()`: Download and convert caption file (lines 1510-1544)
- `convert()`: Convert VTT to SRT format (`vtt_to_srt.py` lines 8-20)
- `download_aria()`: Download file via aria2c (lines 1480-1507)

### Key Variables

- `dl_captions`: Flag to enable caption downloads
- `caption_locale`: Language filter (default: "en")
- `keep_vtt`: Flag to keep VTT files after conversion
- `subtitles`: List of subtitle objects from lecture

### Key Locations

- Subtitle extraction: `_parse_lecture()` lines 1089-1092, 1127-1129
- Caption processing: `parse_new()` lines 1841-1848
- Download: `process_caption()` line 1527
- Conversion: `process_caption()` lines 1536-1544

---

## Summary

### Caption Download Process

1. **Extract** → Subtitle data from asset.captions
2. **Filter** → By language (--lang flag)
3. **Download** → Caption file via aria2c
4. **Convert** → VTT to SRT (if needed)
5. **Cleanup** → Delete VTT (unless --keep-vtt)

### Key Features

- ✅ Multiple language support
- ✅ Automatic VTT to SRT conversion
- ✅ Retry logic (up to 3 attempts)
- ✅ Skip already downloaded files
- ✅ Option to keep VTT files
- ✅ Non-blocking error handling

### Supported Formats

- **Input:** VTT (WebVTT), SRT (SubRip)
- **Output:** SRT (SubRip) format
- **Conversion:** Automatic VTT → SRT

The caption download feature provides flexible subtitle management with automatic format conversion and language filtering.
