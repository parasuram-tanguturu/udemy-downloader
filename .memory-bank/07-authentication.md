# Authentication Guide

This document explains all authentication methods available in the Udemy Downloader.

## Overview

The Udemy Downloader supports multiple authentication methods to access Udemy's API. You must use at least one method to authenticate your requests.

## Authentication Methods

### 1. Bearer Token (Recommended)

Bearer tokens are the preferred authentication method for individual course purchases. They provide direct API access without requiring browser cookies.

#### Method 1a: Command-Line Argument

**Usage:**
```bash
python main.py -c <course-url> -b <bearer_token>
```

**Example:**
```bash
python main.py -c https://www.udemy.com/course/example -b FGKGYFgPNQEcDqRAZn8VQ0HLNv8VEeINzumCMW6b
```

**How it works:**
- Token is passed directly via `-b` or `--bearer` flag
- Sets authentication headers:
  ```python
  {
      "x-udemy-bearer-token": bearer_token,
      "authorization": f"Bearer {bearer_token}"
  }
  ```

#### Method 1b: Environment Variable (.env file)

**Setup:**
1. Create or edit `.env` file in project root
2. Add your bearer token:
   ```env
   UDEMY_BEARER=your_bearer_token_here
   ```

**Usage:**
```bash
# No need to specify -b flag
python main.py -c <course-url>
```

**Advantages:**
- Keeps token out of command history
- Reusable across sessions
- More secure than command-line

**How to Get Bearer Token:**

**Firefox:**
1. Open Udemy in Firefox
2. Press F12 to open DevTools
3. Go to Network tab
4. Filter by "XHR"
5. Visit any Udemy page
6. Look for requests to `api-2.0`
7. Check Request Headers
8. Find `authorization: Bearer <token>`
9. Copy the token value

**Chrome:**
1. Open Udemy in Chrome
2. Press F12 to open DevTools
3. Go to Network tab
4. Filter by "Fetch/XHR"
5. Visit any Udemy page
6. Click on any API request
7. Go to Headers tab
8. Find `authorization: Bearer <token>` in Request Headers
9. Copy the token value

**Reference Guides:**
- Firefox: [Udemy-DL Guide](https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-491903900)
- Chrome: [Udemy-DL Guide](https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-492569372)

---

### 2. Browser Cookies (Automatic Extraction)

Browser cookies are useful for subscription courses or when bearer tokens are unavailable. The tool can automatically extract cookies from your browser.

#### Supported Browsers

```bash
python main.py -c <course-url> --browser chrome
python main.py -c <course-url> --browser firefox
python main.py -c <course-url> --browser opera
python main.py -c <course-url> --browser edge
python main.py -c <course-url> --browser brave
python main.py -c <course-url> --browser chromium
python main.py -c <course-url> --browser vivaldi
python main.py -c <course-url> --browser safari
```

#### How It Works

The tool uses `browser_cookie3` library to extract cookies from your browser's cookie database:

```python
if browser == "chrome":
    cj = browser_cookie3.chrome()
elif browser == "firefox":
    cj = browser_cookie3.firefox()
elif browser == "opera":
    cj = browser_cookie3.opera()
# ... etc
```

**Requirements:**
- Browser must be installed
- You must be logged into Udemy in that browser
- Browser must allow cookie access

**Use Cases:**
- Subscription-based courses
- Alternative to bearer token
- When bearer token expires
- Testing different accounts

**Example:**
```bash
python main.py -c https://www.udemy.com/course/example --browser chrome --download-captions
```

---

### 3. Cookie File (Netscape Format)

For manual cookie management or when browser extraction doesn't work, you can export cookies to a file.

#### Setup

1. Export cookies from browser to `cookies.txt` in Netscape format
2. Place `cookies.txt` in project root directory

#### Usage

```bash
python main.py -c <course-url> --browser file
```

**How it works:**
```python
elif browser == "file":
    cj = MozillaCookieJar("cookies.txt")
    cj.load()
```

**Cookie File Format (Netscape):**
```
# Netscape HTTP Cookie File
.udemy.com	TRUE	/	FALSE	1735689600	access_token	your_token_here
.udemy.com	TRUE	/	FALSE	1735689600	csrftoken	your_csrf_token
```

**Tools to Export Cookies:**
- Browser extensions (e.g., "Get cookies.txt LOCALLY")
- Manual export from browser DevTools
- Cookie export tools

---

## Authentication Priority

The tool checks authentication methods in this order:

1. **Command-line bearer token** (`-b` flag)
2. **Environment variable** (`.env` file with `UDEMY_BEARER`)
3. **Browser cookies** (`--browser` flag)

**Code Flow:**
```python
# 1. Check command-line
if bearer_token:
    # Use bearer token
    udemy.session._session.headers.update({
        "x-udemy-bearer-token": bearer_token,
        "authorization": f"Bearer {bearer_token}"
    })
# 2. Check .env file
elif not bearer_token:
    bearer_token = os.getenv("UDEMY_BEARER")
    
# 3. Check browser
elif browser:
    # Extract cookies from browser
    logger.info("> Using browser cookies for authentication")
    
# 4. Error if none provided
else:
    logger.fatal("> use a bearer token or specify --browser")
    sys.exit(1)
```

---

## Authentication Headers

### Bearer Token Headers

When using bearer token, these headers are set:

```python
{
    "x-udemyandroid-skip-local-cache": "true",
    "cache-control": "no-cache",
    "x-udemy-bearer-token": bearer_token,
    "authorization": f"Bearer {bearer_token}"
}
```

### Cookie-Based Headers

When using browser cookies:

```python
{
    "x-udemyandroid-skip-local-cache": "true",
    "cache-control": "no-cache"
}
# Cookies are sent via Cookie header automatically
```

### Base Headers (Always Present)

All requests include these base headers (from `constants.py`):

```python
{
    "User-Agent": "okhttp/4.12.0 UdemyAndroid 9.51.2(594) (phone)",
    "Accept-Encoding": "gzip",
    "x-mobile-visit-enabled": "true",
    "x-udemy-client-secret": CLIENT_SECRET,
    "authorization": "Basic {BASIC_AUTH}",  # Basic auth for API
    "x-udemy-client-id": CLIENT_ID,
    "accept-language": "en_US",
    "x-version-name": "9.51.2",
    "x-client-name": "Udemy-Android"
}
```

---

## Session Initialization

Before making API calls, the tool performs a "visit" request:

```python
portal_name = udemy.extract_portal_name(course_url)
visit_status = udemy.session.visit(portal_name)
```

**Purpose:**
- Gets Cloudflare bot protection cookies
- Initializes session with Udemy
- Required before any API calls

**Endpoint:**
```
GET https://{portal_name}.udemy.com/api-2.0/visits/current/
```

---

## Method Comparison

| Method | Ease of Use | Security | Subscription Support | Best For |
|--------|-------------|----------|---------------------|----------|
| **Bearer Token (CLI)** | ⭐⭐⭐ Easy | ⭐⭐ Medium | ❌ No | Quick testing |
| **Bearer Token (.env)** | ⭐⭐⭐ Easy | ⭐⭐⭐ High | ❌ No | Production use |
| **Browser Cookies** | ⭐⭐ Medium | ⭐⭐ Medium | ✅ Yes | Subscription courses |
| **Cookie File** | ⭐ Hard | ⭐ Low | ✅ Yes | Manual control |

---

## Troubleshooting

### "use a bearer token or specify --browser"

**Problem:** No authentication method provided

**Solution:**
- Add `-b <token>` flag, OR
- Set `UDEMY_BEARER` in `.env` file, OR
- Use `--browser <browser_name>`

### "Visit request failed"

**Problem:** Cannot initialize session

**Solutions:**
- Check internet connection
- Verify bearer token is valid
- Ensure browser is logged into Udemy (if using cookies)
- Try different browser

### "Failed to find the course, are you enrolled?"

**Problem:** Authentication succeeded but course not found

**Solutions:**
- Verify you're enrolled in the course
- Check course URL is correct
- Try refreshing bearer token
- For subscription courses, use `--browser` method

### Browser Cookie Extraction Fails

**Problem:** Cannot extract cookies from browser

**Solutions:**
- Ensure browser is installed
- Make sure you're logged into Udemy in that browser
- Try different browser
- Use cookie file method instead
- Check browser permissions

---

## Security Best Practices

1. **Never commit tokens to git**
   - Add `.env` to `.gitignore`
   - Don't hardcode tokens in code

2. **Use .env file for production**
   - More secure than command-line
   - Keeps tokens out of shell history

3. **Rotate tokens regularly**
   - Bearer tokens can expire
   - Update `.env` file when needed

4. **Protect cookie files**
   - Don't share `cookies.txt`
   - Treat it like a password

5. **Use least privilege**
   - Only grant access to courses you need
   - Don't use admin accounts

---

## Code References

### Key Functions

- `Udemy.__init__()`: Initializes authentication
- `UdemyAuth`: Handles authentication logic
- `Session.visit()`: Initializes session with Udemy
- `extract_portal_name()`: Extracts portal from URL

### Key Files

- `main.py`: Authentication logic (lines 403-441, 2040-2060)
- `constants.py`: Base headers and client credentials
- `.env`: Environment variable storage (user-created)

---

## Examples

### Example 1: Bearer Token from Command Line

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  -b FGKGYFgPNQEcDqRAZn8VQ0HLNv8VEeINzumCMW6b \
  --download-captions
```

### Example 2: Bearer Token from .env

```bash
# .env file
UDEMY_BEARER=FGKGYFgPNQEcDqRAZn8VQ0HLNv8VEeINzumCMW6b

# Command
python main.py -c https://www.udemy.com/course/example --download-captions
```

### Example 3: Browser Cookies

```bash
python main.py \
  -c https://www.udemy.com/course/example \
  --browser chrome \
  --download-captions \
  --download-assets
```

### Example 4: Cookie File

```bash
# Export cookies to cookies.txt first, then:
python main.py \
  -c https://www.udemy.com/course/example \
  --browser file \
  --info
```

---

## Additional Resources

- [Udemy-DL Authentication Guide](https://github.com/r0oth3x49/udemy-dl/issues/389)
- [browser_cookie3 Documentation](https://github.com/borisbabic/browser_cookie3)
- [Udemy API Documentation](https://www.udemy.com/developers/)
