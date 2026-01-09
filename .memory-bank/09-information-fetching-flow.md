# Information Fetching Flow

This document explains how course information is fetched from Udemy's API with detailed visual flow diagrams.

## Overview

The information fetching process involves multiple API calls to retrieve course metadata, curriculum structure, and lecture details. This document covers the complete flow from URL input to parsed course data.

---

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START: Course URL                         │
│              https://www.udemy.com/course/example            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Initialize Session & Authentication                  │
│ ─────────────────────────────────────────────────────────── │
│ • Extract portal_name from URL                               │
│ • Make visit request (Cloudflare cookies)                    │
│ • Set authentication headers (Bearer token or cookies)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Extract Course Info (Find Course ID)                │
│ ─────────────────────────────────────────────────────────── │
│ • Parse course name/slug from URL                            │
│ • Fetch user's subscribed courses                            │
│ • Match course by name or ID                                 │
│ • Get course_id and basic metadata                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Fetch Course Curriculum                              │
│ ─────────────────────────────────────────────────────────── │
│ • Call curriculum items API (with pagination)                │
│ • Get all chapters, lectures, quizzes                        │
│ • Parse and organize curriculum structure                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Process & Parse Data                                │
│ ─────────────────────────────────────────────────────────── │
│ • Organize into chapters                                     │
│ • Parse lecture metadata                                     │
│ • Extract sources, assets, captions                         │
│ • Build udemy_object structure                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL: udemy_object                      │
│         (Ready for download or info display)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Flow

### Step 1: Session Initialization & Authentication

```
┌─────────────────────────────────────────────────────────────┐
│              SESSION INITIALIZATION                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1.1: Extract Portal Name                                     │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   URL: https://www.udemy.com/course/example                  │
│                                                              │
│   Regex: r"(?://(?P<portal_name>.+?).udemy.com)"            │
│                                                              │
│   Result: portal_name = "www"                               │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1.2: Visit Request (Cloudflare Protection)                  │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   GET https://{portal_name}.udemy.com/api-2.0/visits/current/│
│                                                              │
│   Purpose:                                                   │
│   • Get Cloudflare bot protection cookies                    │
│   • Initialize session with Udemy                            │
│   • Required before any API calls                           │
│                                                              │
│   Response: Session cookies                                  │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1.3: Set Authentication Headers                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   IF Bearer Token:                                           │
│   ┌────────────────────────────────────────────┐           │
│   │ {                                          │           │
│   │   "x-udemy-bearer-token": "{token}",      │           │
│   │   "authorization": "Bearer {token}"        │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   IF Browser Cookies:                                        │
│   ┌────────────────────────────────────────────┐           │
│   │ Cookies sent automatically via Cookie      │           │
│   │ header (extracted from browser)             │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ✅ Session Ready
```

---

### Step 2: Course Discovery & Info Extraction

```
┌─────────────────────────────────────────────────────────────┐
│           COURSE DISCOVERY FLOW                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2.1: Parse Course URL                                        │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   URL: https://www.udemy.com/course/opentelemetry-foundations│
│                                                              │
│   Regex: r"(?://(?P<portal_name>.+?).udemy.com/...          │
│          (?P<name_or_id>[a-zA-Z0-9_-]+))"                   │
│                                                              │
│   Extracted:                                                 │
│   • portal_name = "www"                                      │
│   • course_name = "opentelemetry-foundations"                │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2.2: Fetch User's Subscribed Courses                        │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   API Call 1: Subscribed Courses                              │
│   ┌────────────────────────────────────────────┐           │
│   │ GET /api-2.0/users/me/subscribed-courses  │           │
│   │ ?fields[course]=id,url,title,published_title│          │
│   │ &page_size=10000                           │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   API Call 2: Subscription Enrollments                      │
│   ┌────────────────────────────────────────────┐           │
│   │ GET /api-2.0/users/me/                     │           │
│   │   subscription-course-enrollments           │           │
│   │ ?fields[course]=...&page_size=50            │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   Combined Results:                                          │
│   ┌────────────────────────────────────────────┐           │
│   │ [                                          │           │
│   │   {                                        │           │
│   │     "id": 6195287,                        │           │
│   │     "published_title": "opentelemetry-...",│           │
│   │     "title": "OpenTelemetry Foundations"   │           │
│   │   },                                       │           │
│   │   ... (all user's courses)                 │           │
│   │ ]                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2.3: Match Course by Name or ID                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Search Logic:                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ FOR each course in results:                 │           │
│   │   IF course_name == course.published_title  │           │
│   │      OR course_name == course.id:           │           │
│   │     RETURN course                           │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   IF NOT FOUND:                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ Try archived courses                       │           │
│   │ GET /api-2.0/users/me/subscribed-courses  │           │
│   │   ?is_archived=true                        │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   IF STILL NOT FOUND:                                        │
│   ┌────────────────────────────────────────────┐           │
│   │ ERROR: "Failed to find the course,         │           │
│   │        are you enrolled?"                  │           │
│   │ EXIT                                       │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2.4: Extract Course Metadata                                │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   From Matched Course:                                        │
│   ┌────────────────────────────────────────────┐           │
│   │ {                                          │           │
│   │   "id": 6195287,                           │           │
│   │   "title": "OpenTelemetry Foundations...", │           │
│   │   "published_title": "opentelemetry-...", │           │
│   │   ... (other metadata)                     │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   Return:                                                    │
│   • course_id = 6195287                                      │
│   • course_info = { ... }                                    │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ✅ Course ID Found
```

---

### Step 3: Curriculum Fetching (With Pagination)

```
┌─────────────────────────────────────────────────────────────┐
│           CURRICULUM FETCHING FLOW                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3.1: Build Curriculum API URL                                │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   URL Template:                                              │
│   https://{portal_name}.udemy.com/api-2.0/                  │
│     courses/{course_id}/subscriber-curriculum-items/         │
│                                                              │
│   Parameters:                                                │
│   ┌────────────────────────────────────────────┐           │
│   │ fields[lecture]=title,object_index,        │           │
│   │   created,asset,supplementary_assets,      │           │
│   │   description,download_url                  │           │
│   │ fields[quiz]=title,object_index,type       │           │
│   │ fields[practice]=title,object_index         │           │
│   │ fields[chapter]=title,object_index         │           │
│   │ fields[asset]=title,filename,asset_type,   │           │
│   │   status,is_external,media_license_token,  │           │
│   │   course_is_drmed,media_sources,captions,  │           │
│   │   slides,slide_urls,download_urls,        │           │
│   │   external_url,stream_urls,@min,status,   │           │
│   │   delayed_asset_message,processing_errors,│           │
│   │   body                                     │           │
│   │ caching_intent=True                        │           │
│   │ page_size=200                              │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3.2: Handle Pagination                                       │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Initial Request:                                            │
│   ┌────────────────────────────────────────────┐           │
│   │ GET {url}?page_size=200                    │           │
│   │                                            │           │
│   │ Response:                                   │           │
│   │ {                                          │           │
│   │   "count": 78,                             │           │
│   │   "next": "https://...?page=2",            │           │
│   │   "results": [ ... 200 items ... ]         │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   Pagination Loop:                                           │
│   ┌────────────────────────────────────────────┐           │
│   │ WHILE response.next exists:                 │           │
│   │   • GET response.next                       │           │
│   │   • Append results to combined list         │           │
│   │   • Update page counter                     │           │
│   │   • Log: "Downloading data page X/Y"        │           │
│   │                                            │           │
│   │ Example:                                    │           │
│   │ Page 1: 200 items                           │           │
│   │ Page 2: 200 items                           │           │
│   │ ...                                         │           │
│   │ Page N: Remaining items                     │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   Final Combined Result:                                      │
│   ┌────────────────────────────────────────────┐           │
│   │ {                                          │           │
│   │   "count": 78,                             │           │
│   │   "next": null,                            │           │
│   │   "results": [                              │           │
│   │     ... (all 78 items combined) ...        │           │
│   │   ]                                        │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ✅ All Curriculum Data Retrieved
```

---

### Step 4: Data Processing & Organization

```
┌─────────────────────────────────────────────────────────────┐
│           DATA PROCESSING FLOW                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4.1: Initialize udemy_object                                 │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Structure:                                                  │
│   ┌────────────────────────────────────────────┐           │
│   │ {                                          │           │
│   │   "course_id": 6195287,                    │           │
│   │   "title": "OpenTelemetry Foundations...", │           │
│   │   "course_title": "opentelemetry-...",     │           │
│   │   "chapters": [],                          │           │
│   │   "total_chapters": 0,                     │           │
│   │   "total_lectures": 0                      │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4.2: Process Curriculum Items                                │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   FOR each item in curriculum.results:                       │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ IF item._class == "chapter":                │           │
│   │   • Create new chapter entry                │           │
│   │   • Set chapter_index, chapter_title        │           │
│   │   • Initialize lectures array               │           │
│   │   • Reset lecture_counter                   │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ IF item._class == "lecture":                │           │
│   │   • Parse lecture data                      │           │
│   │   • Extract asset, sources, captions        │           │
│   │   • Add to current chapter's lectures       │           │
│   │   • Increment lecture_counter               │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ IF item._class == "quiz":                   │           │
│   │   • Add quiz to current chapter             │           │
│   │   • Mark as quiz type                       │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4.3: Parse Lecture Details                                   │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Function: udemy._parse_lecture(lecture)                    │
│                                                              │
│   Process:                                                   │
│   ┌────────────────────────────────────────────┐           │
│   │ 1. Extract asset data                      │           │
│   │    • asset_type (video, article, etc.)     │           │
│   │    • stream_urls (for non-DRM)             │           │
│   │    • media_sources (for DRM)               │           │
│   │                                            │           │
│   │ 2. Extract sources                         │           │
│   │    • Parse HLS playlists (if present)      │           │
│   │    • Sort by quality                       │           │
│   │    • Extract download URLs                 │           │
│   │                                            │           │
│   │ 3. Extract captions                        │           │
│   │    • Get caption tracks                    │           │
│   │    • Extract languages                     │           │
│   │    • Get download URLs                     │           │
│   │                                            │           │
│   │ 4. Extract supplementary assets           │           │
│   │    • PDFs, code files, etc.                │           │
│   │    • Get download URLs                     │           │
│   │                                            │           │
│   │ 5. Determine DRM status                    │           │
│   │    • Check media_sources vs stream_urls    │           │
│   │    • Set is_encrypted flag                 │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4.4: Finalize udemy_object                                  │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Calculate Totals:                                          │
│   ┌────────────────────────────────────────────┐           │
│   │ total_chapters = len(chapters)              │           │
│   │ total_lectures = sum(                       │           │
│   │   [ch.lecture_count for ch in chapters]     │           │
│   │ )                                           │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   Final Structure:                                           │
│   ┌────────────────────────────────────────────┐           │
│   │ {                                          │           │
│   │   "course_id": 6195287,                    │           │
│   │   "title": "OpenTelemetry Foundations...", │           │
│   │   "course_title": "opentelemetry-...",     │           │
│   │   "total_chapters": 9,                     │           │
│   │   "total_lectures": 69,                     │           │
│   │   "chapters": [                            │           │
│   │     {                                      │           │
│   │       "chapter_index": 1,                  │           │
│   │       "chapter_title": "01 - Introduction",│          │
│   │       "lecture_count": 5,                  │           │
│   │       "lectures": [                        │           │
│   │         {                                  │           │
│   │           "lecture_title": "...",         │           │
│   │           "sources": [...],                │           │
│   │           "is_encrypted": false,          │           │
│   │           "subtitles": [...],              │           │
│   │           "assets": [...]                 │           │
│   │         },                                 │           │
│   │         ...                                │           │
│   │       ]                                    │           │
│   │     },                                     │           │
│   │     ...                                    │           │
│   │   ]                                        │           │
│   │ }                                          │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ✅ udemy_object Ready
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: Course URL                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  Extract portal_name &           │
        │  course_name from URL            │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Visit API (Cloudflare)          │
        │  GET /api-2.0/visits/current/   │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Set Auth Headers                │
        │  (Bearer token or cookies)       │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Fetch Subscribed Courses        │
        │  GET /api-2.0/users/me/         │
        │    subscribed-courses           │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Match Course by Name/ID         │
        │  (Try archived if not found)     │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Get course_id & metadata         │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Fetch Curriculum (Page 1)       │
        │  GET /api-2.0/courses/{id}/     │
        │    subscriber-curriculum-items/ │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Check if more pages exist        │
        │  (response.next != null)         │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │   YES        │    │     NO       │
    │              │    │              │
    │ Fetch Page 2 │    │ Continue     │
    │ Fetch Page 3 │    │ Processing   │
    │ ...          │    │              │
    └──────┬───────┘    └──────┬───────┘
           │                  │
           └──────────┬───────┘
                      │
                      ▼
        ┌──────────────────────────────────┐
        │  Combine All Pages               │
        │  (All curriculum items)          │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Process Each Item               │
        │  • Chapters                      │
        │  • Lectures                      │
        │  • Quizzes                       │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Parse Lecture Data              │
        │  • Sources                       │
        │  • Captions                      │
        │  • Assets                        │
        │  • DRM status                    │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Build udemy_object              │
        │  (Organized structure)           │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  Optional: Save to File          │
        │  (--save-to-file)                │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  OUTPUT: udemy_object             │
        │  (Ready for use)                 │
        └──────────────────────────────────┘
```

---

## API Endpoints Used

### 1. Visit Endpoint

```
GET https://{portal_name}.udemy.com/api-2.0/visits/current/
```

**Purpose:** Initialize session, get Cloudflare cookies

**Response:**
```json
{
  "visitor": {...},
  "country": "US",
  ...
}
```

---

### 2. Subscribed Courses Endpoint

```
GET https://{portal_name}.udemy.com/api-2.0/users/me/subscribed-courses
?fields[course]=id,url,title,published_title
&ordering=-last_accessed,-access_time
&page=1
&page_size=10000
```

**Purpose:** Get all courses user is subscribed to

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 6195287,
      "title": "OpenTelemetry Foundations...",
      "published_title": "opentelemetry-foundations",
      "url": "/course/opentelemetry-foundations/"
    },
    ...
  ]
}
```

---

### 3. Subscription Enrollments Endpoint

```
GET https://{portal_name}.udemy.com/api-2.0/users/me/subscription-course-enrollments
?fields[course]=...
&page_size=50
```

**Purpose:** Get subscription-based course enrollments

---

### 4. Course Info Endpoint

```
GET https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/
```

**Purpose:** Get detailed course metadata

**Response:**
```json
{
  "id": 6195287,
  "title": "OpenTelemetry Foundations Hands-On Guide to Observability",
  "published_title": "opentelemetry-foundations",
  "headline": "...",
  "num_published_lectures": 69,
  ...
}
```

---

### 5. Curriculum Items Endpoint

```
GET https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/
?fields[lecture]=title,object_index,created,asset,supplementary_assets,description,download_url
&fields[quiz]=title,object_index,type
&fields[practice]=title,object_index
&fields[chapter]=title,object_index
&fields[asset]=title,filename,asset_type,status,is_external,media_license_token,course_is_drmed,media_sources,captions,slides,slide_urls,download_urls,external_url,stream_urls,@min,status,delayed_asset_message,processing_errors,body
&caching_intent=True
&page_size=200
```

**Purpose:** Get all curriculum items (chapters, lectures, quizzes)

**Response (Paginated):**
```json
{
  "count": 78,
  "next": "https://...?page=2",
  "results": [
    {
      "_class": "chapter",
      "object_index": 1,
      "title": "01 - Introduction",
      ...
    },
    {
      "_class": "lecture",
      "object_index": 1,
      "title": "001 About this Course",
      "asset": {
        "asset_type": "Video",
        "stream_urls": {...},
        "media_sources": {...},
        "captions": [...]
      },
      ...
    },
    ...
  ]
}
```

---

## Pagination Handling

### How Pagination Works

```
┌─────────────────────────────────────────────────────────────┐
│                    PAGINATION FLOW                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Initial Request                                      │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   GET {url}?page_size=200                                    │
│                                                              │
│   Response:                                                  │
│   {                                                          │
│     "count": 78,        ← Total items                       │
│     "next": "url?page=2", ← Next page URL                   │
│     "results": [200 items]                                   │
│   }                                                          │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Calculate Page Count                                 │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   est_page_count = ceil(count / page_size)                   │
│   est_page_count = ceil(78 / 200) = 1 page                  │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Pagination Loop                                      │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   WHILE response.next != null:                               │
│     ┌────────────────────────────────────┐                 │
│     │ Log: "Downloading data page X/Y"   │                 │
│     │ GET response.next                  │                 │
│     │ Append results to combined list    │                 │
│     │ Update: response.next              │                 │
│     └────────────────────────────────────┘                 │
│                                                              │
│   Example with 450 items (page_size=200):                    │
│   • Page 1: 200 items, next exists                          │
│   • Page 2: 200 items, next exists                          │
│   • Page 3: 50 items, next = null (done)                     │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Combine Results                                      │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│   Final data.results = [                                     │
│     ... (all items from page 1) ...,                        │
│     ... (all items from page 2) ...,                        │
│     ... (all items from page 3) ...                         │
│   ]                                                          │
│                                                              │
│   Total: 450 items combined                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Caching Support

### Save to File (`--save-to-file`)

```
┌─────────────────────────────────────────────────────────────┐
│                    SAVE TO FILE FLOW                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ After fetching curriculum:                                   │
│                                                              │
│   1. Save raw curriculum JSON:                              │
│      saved/course_content.json                               │
│                                                              │
│   2. Save parsed udemy_object:                               │
│      saved/_udemy.json                                       │
│                                                              │
│   Note: Asset URLs expire after time,                       │
│         cache has limited lifetime                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Load from File (`--load-from-file`)

```
┌─────────────────────────────────────────────────────────────┐
│                    LOAD FROM FILE FLOW                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Skip API calls:                                              │
│                                                              │
│   1. Load curriculum from:                                   │
│      saved/course_content.json                               │
│                                                              │
│   2. Load parsed data from:                                  │
│      saved/_udemy.json                                       │
│                                                              │
│   Benefit: Much faster (no network calls)                   │
│   Warning: URLs may be expired                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Lecture Parsing Details

### What Gets Parsed from Each Lecture

```
┌─────────────────────────────────────────────────────────────┐
│              LECTURE DATA EXTRACTION                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ From lecture.data.asset:                                     │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 1. Asset Type                              │           │
│   │    • "Video"                               │           │
│   │    • "Article"                             │           │
│   │    • "Audio"                               │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 2. Video Sources (Non-DRM)                 │           │
│   │    • stream_urls.Video                     │           │
│   │    • HLS playlists                         │           │
│   │    • Direct video URLs                     │           │
│   │    • Quality levels                        │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 3. Media Sources (DRM)                     │           │
│   │    • media_sources (DASH)                  │           │
│   │    • MPD manifest URLs                     │           │
│   │    • Format IDs                            │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 4. Captions/Subtitles                       │           │
│   │    • Caption tracks                        │           │
│   │    • Languages                             │           │
│   │    • Download URLs                         │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 5. Supplementary Assets                    │           │
│   │    • PDFs, code files, etc.                │           │
│   │    • Download URLs                         │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
│   ┌────────────────────────────────────────────┐           │
│   │ 6. DRM Status                               │           │
│   │    • Check media_sources vs stream_urls    │           │
│   │    • Set is_encrypted flag                 │           │
│   └────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOW                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  API Request                     │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  Success     │    │   Error      │
    │  (200 OK)    │    │              │
    └──────┬───────┘    └──────┬───────┘
           │                   │
           │                   ▼
           │          ┌──────────────────┐
           │          │ Connection Error  │
           │          │ • Retry logic    │
           │          │ • Log error      │
           │          │ • Exit if fatal  │
           │          └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Parse JSON   │
    └──────┬───────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│ Valid   │   │ Invalid│
│ JSON    │   │ JSON   │
└────┬────┘   └───┬────┘
     │            │
     │            ▼
     │    ┌───────────────┐
     │    │ Log Error     │
     │    │ Handle Gracefully│
     │    └───────────────┘
     │
     ▼
┌───────────────┐
│ Continue      │
│ Processing    │
└───────────────┘
```

---

## Performance Considerations

### 1. Pagination Impact

```
Small Course (< 200 items):
┌─────────────────────────────────────┐
│ 1 API call                          │
│ ~2-5 seconds                        │
└─────────────────────────────────────┘

Large Course (> 200 items):
┌─────────────────────────────────────┐
│ Multiple API calls                  │
│ ~5-15 seconds (depends on size)    │
└─────────────────────────────────────┘
```

### 2. Lecture Parsing

```
Simple Lecture (Basic info only):
┌─────────────────────────────────────┐
│ Fast parsing                        │
│ ~0.1 seconds per lecture            │
└─────────────────────────────────────┘

Complex Lecture (HLS parsing):
┌─────────────────────────────────────┐
│ Slower parsing                      │
│ ~1-3 seconds per lecture            │
│ (if --skip-hls not used)            │
└─────────────────────────────────────┘
```

### 3. Caching Benefits

```
Without Cache:
┌─────────────────────────────────────┐
│ Full API calls                      │
│ ~10-30 seconds                      │
└─────────────────────────────────────┘

With Cache (--load-from-file):
┌─────────────────────────────────────┐
│ Load from disk                      │
│ ~1-2 seconds                        │
└─────────────────────────────────────┘
```

---

## Code References

### Key Functions

- `main()`: Orchestrates the entire flow (lines 2003-2260)
- `_extract_course_info()`: Finds course by URL (lines 1017-1041)
- `_extract_course_curriculum()`: Fetches curriculum (line 949-952)
- `_handle_pagination()`: Handles paginated requests (lines 873-914)
- `_get_courses()`: Gets user's courses (lines 932-935)
- `_parse_lecture()`: Parses lecture data (lines 1043+)
- `extract_course_name()`: Parses URL (lines 857-866)
- `extract_portal_name()`: Extracts portal (lines 868-871)

### Key API Endpoints

- Visit: `URLS.VISIT`
- Subscribed Courses: `URLS.MY_COURSES`
- Subscription Enrollments: `URLS.SUBSCRIPTION_COURSES`
- Course Info: `URLS.COURSE`
- Curriculum: `URLS.CURRICULUM_ITEMS`

---

## Summary

### Information Fetching Process

1. **Initialize** → Extract portal, visit API, set auth
2. **Discover** → Find course in user's subscriptions
3. **Fetch** → Get curriculum with pagination
4. **Parse** → Organize into chapters/lectures
5. **Process** → Extract sources, captions, assets
6. **Output** → Ready-to-use `udemy_object`

### Key Features

- ✅ Automatic pagination handling
- ✅ Course discovery from subscriptions
- ✅ Fallback to archived courses
- ✅ Caching support (save/load)
- ✅ Error handling and retries
- ✅ Comprehensive data extraction

The fetched information is used for:
- Course info display (`--info`)
- Curriculum markdown generation (`--curriculum-only`)
- Video downloads (full process)
