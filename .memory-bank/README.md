# Memory Bank

This directory contains comprehensive documentation about the Udemy Downloader project. The memory bank is organized into several focused documents:

## Documentation Index

### [00-project-overview.md](./00-project-overview.md)

- Project purpose and features
- Legal disclaimers
- Credits and acknowledgments

### [01-architecture.md](./01-architecture.md)

- Core components and their roles
- Data flow diagrams
- External dependencies
- System architecture overview

### [02-key-files.md](./02-key-files.md)

- Detailed file reference
- Purpose of each major file
- Key functions and classes
- Configuration files

### [03-workflows.md](./03-workflows.md)

- Step-by-step workflow documentation
- Authentication flow
- Course discovery process
- Download and processing flows
- Caching mechanisms

### [04-configuration.md](./04-configuration.md)

- Setup instructions
- Command-line arguments reference
- Configuration file formats
- Output structure
- System requirements

### [05-development-patterns.md](./05-development-patterns.md)

- Code style and conventions
- Common patterns
- Data structures
- API interaction patterns
- Best practices

### [06-troubleshooting.md](./06-troubleshooting.md)

- Common issues and solutions
- Debugging tips
- Known limitations
- Getting help

### [07-authentication.md](./07-authentication.md)

- Authentication methods overview
- Bearer token setup and usage
- Browser cookie extraction
- Cookie file management
- Security best practices
- Troubleshooting authentication issues

### [08-video-download-flow.md](./08-video-download-flow.md)

- Complete video download process visualization
- Non-DRM vs DRM download flows
- Step-by-step flow diagrams
- Quality selection logic
- Tool usage (yt-dlp, aria2c, ffmpeg)
- Error handling and optimization

### [09-information-fetching-flow.md](./09-information-fetching-flow.md)

- Complete information fetching process visualization
- API endpoint details and usage
- Course discovery and matching flow
- Pagination handling
- Data parsing and organization
- Caching mechanisms
- Error handling

### [10-curriculum-creation-flow.md](./10-curriculum-creation-flow.md)

- Curriculum markdown generation process visualization
- Step-by-step content building flow
- Enhanced features: course details, instructor info, social links
- Learning objectives, prerequisites, target audience sections
- Chapter and lecture processing with type and duration
- Quick navigation table with clickable links
- Markdown format details
- Performance characteristics
- Error handling
- Usage examples

### [11-caption-download-flow.md](./11-caption-download-flow.md)

- Caption/subtitle download process visualization
- Subtitle extraction from asset data
- Language filtering logic
- VTT to SRT conversion flow
- Download and retry mechanisms
- File naming conventions
- Error handling
- Usage examples

## How to Use This Memory Bank

1. **For New Developers**: Start with `00-project-overview.md` and `01-architecture.md`
2. **For Configuration**: See `04-configuration.md`
3. **For Authentication**: See `07-authentication.md`
4. **For Understanding Flows**: Read `03-workflows.md`
5. **For Information Fetching**: See `09-information-fetching-flow.md` (API calls and data flow)
6. **For Video Downloads**: See `08-video-download-flow.md` (visual flow diagrams)
7. **For Curriculum Generation**: See `10-curriculum-creation-flow.md` (markdown generation flow)
8. **For Caption Downloads**: See `11-caption-download-flow.md` (subtitle download and conversion flow)
9. **For Debugging**: Check `06-troubleshooting.md`
10. **For Code Changes**: Reference `05-development-patterns.md` and `02-key-files.md`

## Maintenance

This memory bank should be updated when:

- New features are added
- Architecture changes
- New patterns emerge
- Common issues are discovered
- Configuration options change

## Quick Reference

### Essential Commands

```bash
# Basic download
python main.py -c <course_url> -b <bearer_token>

# With options
python main.py -c <course_url> -b <bearer_token> --download-captions --download-assets -q 720

# Info only
python main.py -c <course_url> -b <bearer_token> --info

# Debug mode
python main.py -c <course_url> -b <bearer_token> --log-level DEBUG
```

### Key Files

- `main.py`: Main application (2165 lines)
- `constants.py`: Configuration constants
- `utils.py`: DRM utilities
- `keyfile.json`: Decryption keys (user-created)

### Important Directories

- `out_dir/`: Download output
- `saved/`: Cached course data
- `logs/`: Application logs
- `temp/`: Temporary processing files
