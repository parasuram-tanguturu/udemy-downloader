# Troubleshooting Guide

## Common Issues

### Authentication Problems

#### "No bearer token was provided"

**Symptoms**: Error message about missing bearer token
**Solutions**:

1. Provide bearer token via `-b` flag
2. Set `UDEMY_BEARER` in `.env` file
3. Use `--browser` flag to extract cookies

#### "Failed to find the course, are you enrolled?"

**Symptoms**: Course lookup fails
**Solutions**:

1. Verify course URL is correct
2. Ensure you're enrolled in the course
3. For subscription courses, use `--subscription-course` flag
4. Try using `--browser` flag for cookie-based auth

#### "Visit request failed"

**Symptoms**: Cloudflare cookie acquisition fails
**Solutions**:

1. Check network connectivity
2. Verify portal name extraction is correct
3. May need to update User-Agent or headers

### DRM/Decryption Issues

#### "Audio key not found for {kid}"

**Symptoms**: Missing decryption key error
**Solutions**:

1. Extract KID from video file manually
2. Add KID and corresponding key to `keyfile.json`
3. Verify key format (hex string, lowercase)
4. Ensure `keyfile.json` is valid JSON

#### "Error extracting video kid"

**Symptoms**: KID extraction fails
**Solutions**:

1. Verify MP4 file was downloaded correctly
2. Check if file is actually encrypted (may be unencrypted)
3. Ensure `mp4parse.py` and `widevine_pssh_data_pb2.py` are present

#### "Muxing returned a non-zero exit code"

**Symptoms**: FFmpeg decryption/muxing fails
**Solutions**:

1. Verify ffmpeg is installed and in PATH
2. Check decryption keys are correct
3. Verify input files exist and are valid
4. Check ffmpeg has decryption support (may need custom build)

### Download Issues

#### "Aria2c is missing from your system or path!"

**Symptoms**: aria2c not found
**Solutions**:

1. Install aria2c: `brew install aria2` (Mac), `apt install aria2` (Linux)
2. Verify it's in PATH: `which aria2c`
3. Windows: Download from GitHub releases

#### "FFMPEG is missing from your system or path!"

**Symptoms**: ffmpeg not found
**Solutions**:

1. Install ffmpeg
2. Recommended: Use yt-dlp team's custom build for better compatibility
3. Verify it's in PATH: `which ffmpeg`

#### "Shaka Packager is missing"

**Symptoms**: shaka-packager not found
**Solutions**:

1. Download from GitHub releases
2. Add to PATH
3. Note: May not be actively used in current codebase

#### Download fails or hangs

**Symptoms**: Downloads don't complete
**Solutions**:

1. Check network connectivity
2. Reduce `--concurrent-downloads` value
3. Check if URLs have expired (asset links expire)
4. Try `--load-from-file` if you have cached data
5. Check logs for specific error messages

### Quality/Format Issues

#### "Selected quality not available"

**Symptoms**: Requested quality not found
**Solutions**:

1. Program automatically selects closest quality
2. Use `--info` to see available qualities
3. Don't specify `-q` to get best available

#### HLS streams skipped

**Symptoms**: Missing 1080p quality for non-DRM videos
**Solutions**:

1. Remove `--skip-hls` flag (if used)
2. HLS streams typically contain 1080p for non-DRM content

### File System Issues

#### "Path too long" (Windows)

**Symptoms**: File path exceeds Windows limit
**Solutions**:

1. Use `--id-as-course-name` to shorten paths
2. Use `-o` to specify shorter output directory
3. Download to root drive (e.g., `C:\courses`)

#### Permission errors

**Symptoms**: Cannot write files
**Solutions**:

1. Check directory permissions
2. Ensure output directory is writable
3. Run with appropriate permissions

### Encoding Issues

#### H.265 encoding fails

**Symptoms**: Encoding returns non-zero exit code
**Solutions**:

1. Verify ffmpeg has H.265 support: `ffmpeg -codecs | grep hevc`
2. For hardware encoding, ensure CUDA is available
3. Try software encoding without `--use-nvenc`
4. Adjust CRF or preset values

#### "NVIDIA hardware transcoding" not working

**Symptoms**: NVENC encoding fails
**Solutions**:

1. Verify NVIDIA GPU is available
2. Check CUDA is installed
3. Ensure ffmpeg was compiled with NVENC support
4. Fall back to software encoding

### Caption Issues

#### Captions not downloading

**Symptoms**: No subtitle files created
**Solutions**:

1. Use `--download-captions` flag
2. Check if lecture has captions available
3. Verify language code is correct (use `--info` to see available languages)

#### VTT to SRT conversion fails

**Symptoms**: Conversion error
**Solutions**:

1. Check `vtt_to_srt.py` is present
2. Verify VTT file format is valid
3. Use `--keep-vtt` to keep original files for debugging

### Quiz/Asset Issues

#### Quizzes not downloading

**Symptoms**: Quiz HTML files not created
**Solutions**:

1. Use `--download-quizzes` flag
2. Verify quiz templates exist in `templates/` directory

#### Assets not downloading

**Symptoms**: Supplementary files missing
**Solutions**:

1. Use `--download-assets` flag
2. Check if lecture has assets available
3. Verify download URLs haven't expired

## Debugging Tips

### Enable Debug Logging

```bash
python main.py -c <url> --log-level DEBUG
```

### Check Log Files

- Logs are in `logs/` directory
- Timestamped filenames
- Contains detailed error information

### Use Info Mode

```bash
python main.py -c <url> --info
```

- Shows course structure without downloading
- Lists available qualities, captions, etc.

### Verify System Tools

```bash
# Check if tools are available
which ffmpeg
which aria2c
which yt-dlp
which shaka-packager

# Test ffmpeg
ffmpeg -version

# Test aria2c
aria2c -v
```

### Test Authentication

```bash
# Try with browser cookies
python main.py -c <url> --browser chrome --info
```

### Cache Course Data

```bash
# Save course data for debugging
python main.py -c <url> --save-to-file --info

# Inspect saved JSON files
cat saved/course_content.json
cat saved/_udemy.json
```

## Known Limitations

1. **Asset URL Expiration**: Download URLs expire after some time
2. **DRM Keys Required**: Cannot decrypt without user-provided keys
3. **Rate Limiting**: May hit Udemy API rate limits with large courses
4. **Path Length**: Windows has 260 character path limit
5. **Browser Cookie Access**: May require browser to be closed on some systems

## Getting Help

1. Check log files for detailed error messages
2. Use `--log-level DEBUG` for verbose output
3. Verify all system dependencies are installed
4. Test with `--info` flag first
5. Check GitHub issues for similar problems
6. Provide log files when reporting issues
