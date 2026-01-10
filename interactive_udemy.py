#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive wrapper for Udemy Downloader
Provides a menu-driven interface for selecting download options
"""
import os
import re
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import browser_cookie3
        return True
    except ImportError:
        print("=" * 60)
        print("ERROR: Required dependencies are not installed!")
        print("=" * 60)
        print("\nPlease install the required packages by running:")
        print("  pip3 install -r requirements.txt")
        print("\nOr install them individually:")
        print("  pip3 install browser_cookie3")
        print("=" * 60)
        return False


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """Print a nice header"""
    print("=" * 60)
    print("  Udemy Course Downloader - Interactive Mode")
    print("=" * 60)
    print()


def get_user_input(prompt, default=None, required=True):
    """Get user input with optional default value"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        try:
            value = input(full_prompt).strip()
            if value:
                return value
            elif default:
                return default
            elif not required:
                return None
            else:
                print("This field is required. Please enter a value.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def get_yes_no(prompt, default=True):
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    try:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)


def get_menu_choice(prompt, options, default=None):
    """Display a menu and get user choice"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        marker = " [default]" if default and i == default else ""
        print(f"  {i}. {option}{marker}")
    
    while True:
        try:
            choice = input(f"\nSelect option [1-{len(options)}]: ").strip()
            if not choice and default:
                return default
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def get_multi_select(prompt, options, defaults=None):
    """Get multiple selections from user"""
    if defaults is None:
        defaults = []
    
    print(f"\n{prompt}")
    print("(Enter numbers separated by commas, e.g., 1,3,4)")
    for i, option in enumerate(options, 1):
        marker = " [default]" if i in defaults else ""
        print(f"  {i}. {option}{marker}")
    
    while True:
        try:
            response = input(f"\nSelect options (comma-separated): ").strip()
            if not response and defaults:
                return defaults
            
            try:
                selected = [int(x.strip()) for x in response.split(',')]
                valid_selected = [s for s in selected if 1 <= s <= len(options)]
                if valid_selected:
                    return valid_selected
                else:
                    print("Please enter at least one valid option number")
            except ValueError:
                print("Please enter numbers separated by commas")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def extract_course_name_from_url(url):
    """Extract course name/ID from URL for directory prediction"""
    # Try to extract course slug from URL
    match = re.search(r'/course/([^/?]+)', url)
    if match:
        return match.group(1)
    return None


def build_arguments(selections):
    """Build command-line arguments for main.py based on user selections"""
    args = ['python3', 'main.py']
    
    # Required: course URL
    args.extend(['-c', selections['course_url']])
    
    # Bearer token (optional if using browser)
    if selections.get('bearer_token'):
        args.extend(['-b', selections['bearer_token']])
    
    # Browser (if selected)
    if selections.get('browser'):
        args.extend(['--browser', selections['browser']])
    
    # Main action
    if selections['action'] == 'info':
        args.append('--info')
    elif selections['action'] == 'curriculum':
        args.append('--curriculum-only')
    
    # Download options
    if selections.get('skip_lectures'):
        args.append('--skip-lectures')
    
    if selections.get('download_captions'):
        args.append('--download-captions')
        if selections.get('caption_language'):
            args.extend(['-l', selections['caption_language']])
    
    if selections.get('download_assets'):
        args.append('--download-assets')
    
    if selections.get('download_quizzes'):
        args.append('--download-quizzes')
    
    # Quality
    if selections.get('quality'):
        args.extend(['-q', str(selections['quality'])])
    
    # Output directory
    if selections.get('output_dir'):
        args.extend(['-o', selections['output_dir']])
    
    # Chapter filter
    if selections.get('chapter_filter'):
        args.extend(['--chapter', selections['chapter_filter']])
    
    # Other options
    if selections.get('keep_vtt'):
        args.append('--keep-vtt')
    
    if selections.get('skip_hls'):
        args.append('--skip-hls')
    
    if selections.get('subscription_course'):
        args.append('--subscription-course')
    
    if selections.get('id_as_course_name'):
        args.append('--id-as-course-name')
    
    if selections.get('continuous_lecture_numbers'):
        args.append('--continue-lecture-numbers')
    
    if selections.get('concurrent_downloads'):
        args.extend(['-cd', str(selections['concurrent_downloads'])])
    
    if selections.get('use_h265'):
        args.append('--use-h265')
        if selections.get('h265_crf'):
            args.extend(['--h265-crf', str(selections['h265_crf'])])
        if selections.get('h265_preset'):
            args.extend(['--h265-preset', selections['h265_preset']])
        if selections.get('use_nvenc'):
            args.append('--use-nvenc')
    
    if selections.get('log_level'):
        args.extend(['--log-level', selections['log_level']])
    
    return args


def get_output_directory(selections, script_dir):
    """Determine the output directory path"""
    # Check if custom output directory was specified
    if selections.get('output_dir'):
        base_dir = selections['output_dir']
    else:
        base_dir = os.path.join(script_dir, 'out_dir')
    
    # Try to extract course name from URL for prediction
    course_url = selections.get('course_url', '')
    course_slug = extract_course_name_from_url(course_url)
    
    if course_slug:
        # This is a best guess - actual course name might differ
        # The actual course name will be determined by main.py
        predicted_dir = os.path.join(base_dir, course_slug)
        return base_dir, predicted_dir
    
    return base_dir, None


def find_actual_output_directory(base_dir, course_url):
    """Try to find the actual output directory after execution"""
    if not os.path.exists(base_dir):
        return None
    
    # Get the most recently modified directory (likely the course we just downloaded)
    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not dirs:
        return None
    
    # Sort by modification time, most recent first
    dirs_with_time = [
        (d, os.path.getmtime(os.path.join(base_dir, d)))
        for d in dirs
    ]
    dirs_with_time.sort(key=lambda x: x[1], reverse=True)
    
    # Return the most recent directory
    most_recent = dirs_with_time[0][0]
    return os.path.join(base_dir, most_recent)


def main():
    """Main interactive function"""
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    clear_screen()
    print_header()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    selections = {}
    
    # Main action selection
    action_choice = get_menu_choice(
        "What would you like to do?",
        ["Generate curriculum only", "Download course", "View course info only"],
        default=1
    )
    
    action_map = {1: 'curriculum', 2: 'download', 3: 'info'}
    selections['action'] = action_map[action_choice]
    
    # Course URL (required)
    print("\n" + "=" * 60)
    selections['course_url'] = get_user_input("Course URL", required=True)
    
    # Authentication method
    print("\n" + "=" * 60)
    auth_choice = get_menu_choice(
        "Authentication method:",
        ["Bearer token", "Browser cookies", "Skip (use .env file)"],
        default=1
    )
    
    if auth_choice == 1:
        print("\n" + "-" * 60)
        print("NOTE: Bearer token is the same as 'access_token' from browser cookies.")
        print("How to get it:")
        print("  1. Open Udemy in your browser")
        print("  2. Open Developer Tools (F12 or Cmd+Option+I)")
        print("  3. Go to 'Application' tab (Chrome) or 'Storage' tab (Firefox)")
        print("  4. Expand 'Cookies' > select your Udemy domain")
        print("  5. Find 'access_token' cookie and copy its Value")
        print("-" * 60)
        selections['bearer_token'] = get_user_input("Bearer token (access_token from cookies)", required=True)
    elif auth_choice == 2:
        browser_choice = get_menu_choice(
            "Select browser (or 'file' to use cookies from file):",
            ["chrome", "firefox", "opera", "edge", "brave", "chromium", "vivaldi", "safari", "file"],
            default=1
        )
        browsers = ["chrome", "firefox", "opera", "edge", "brave", "chromium", "vivaldi", "safari", "file"]
        selections['browser'] = browsers[browser_choice - 1]
        if selections['browser'] == 'file':
            print("\nNOTE: When using 'file', cookies should be in Netscape format")
            print("and saved as 'cookies.txt' in the project directory.")
    
    # If downloading, get download options
    if selections['action'] == 'download':
        print("\n" + "=" * 60)
        print("Download Options:")
        
        selections['skip_lectures'] = not get_yes_no("Download lectures?", default=True)
        selections['download_captions'] = get_yes_no("Download captions?", default=False)
        if selections['download_captions']:
            selections['caption_language'] = get_user_input(
                "Caption language (e.g., 'en', 'es', 'all')",
                default='en',
                required=False
            )
        
        selections['download_assets'] = get_yes_no("Download assets?", default=False)
        selections['download_quizzes'] = get_yes_no("Download quizzes?", default=False)
        
        # Advanced options
        print("\n" + "=" * 60)
        print("Advanced Options (press Enter to skip):")
        
        quality = get_user_input("Video quality (e.g., 720, 1080)", required=False)
        if quality:
            try:
                selections['quality'] = int(quality)
            except ValueError:
                print("Invalid quality, skipping...")
        
        output_dir = get_user_input("Output directory (leave empty for default: out_dir)", required=False)
        if output_dir:
            selections['output_dir'] = os.path.abspath(os.path.expanduser(output_dir))
        
        chapter_filter = get_user_input(
            "Chapter filter (e.g., '1,3-5,7' or leave empty)",
            required=False
        )
        if chapter_filter:
            selections['chapter_filter'] = chapter_filter
        
        selections['keep_vtt'] = get_yes_no("Keep VTT files?", default=False)
        selections['skip_hls'] = get_yes_no("Skip HLS streams?", default=False)
        selections['subscription_course'] = get_yes_no("Is this a subscription course?", default=False)
        selections['id_as_course_name'] = get_yes_no("Use course ID as directory name?", default=False)
        selections['continuous_lecture_numbers'] = get_yes_no("Use continuous lecture numbering?", default=False)
        
        concurrent = get_user_input("Concurrent downloads (1-30)", default='10', required=False)
        if concurrent:
            try:
                selections['concurrent_downloads'] = int(concurrent)
            except ValueError:
                pass
        
        use_h265 = get_yes_no("Encode with H.265?", default=False)
        if use_h265:
            selections['use_h265'] = True
            crf = get_user_input("H.265 CRF (default: 28)", default='28', required=False)
            if crf:
                try:
                    selections['h265_crf'] = int(crf)
                except ValueError:
                    pass
            preset = get_user_input("H.265 preset (default: medium)", default='medium', required=False)
            if preset:
                selections['h265_preset'] = preset
            selections['use_nvenc'] = get_yes_no("Use NVIDIA hardware encoding?", default=False)
    
    # Log level
    log_level_choice = get_menu_choice(
        "\nLog level:",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=2
    )
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    selections['log_level'] = log_levels[log_level_choice - 1]
    
    # Build and execute command
    args = build_arguments(selections)
    
    print("\n" + "=" * 60)
    print("Executing command:")
    print(" ".join(args))
    print("=" * 60 + "\n")
    
    # Execute main.py
    try:
        result = subprocess.run(
            args, 
            cwd=script_dir, 
            check=False,
            capture_output=False  # Let output stream through
        )
        
        # Determine output directory
        base_dir, _ = get_output_directory(selections, script_dir)
        actual_dir = find_actual_output_directory(base_dir, selections.get('course_url'))
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✓ Download completed successfully!")
        else:
            print("⚠ Process completed with exit code:", result.returncode)
            if result.returncode != 0:
                print("\nTip: If you see 'ModuleNotFoundError', install dependencies with:")
                print("  pip3 install -r requirements.txt")
        
        print("\nOutput directory:")
        if actual_dir and os.path.exists(actual_dir):
            print(f"  {actual_dir}")
            
            # Show contents summary
            if os.path.exists(actual_dir):
                files = list(Path(actual_dir).rglob('*'))
                files = [f for f in files if f.is_file()]
                dirs = [d for d in Path(actual_dir).rglob('*') if d.is_dir()]
                
                print(f"\n  Files: {len(files)}")
                print(f"  Directories: {len(dirs)}")
                
                # Check for curriculum.md
                curriculum_path = os.path.join(actual_dir, 'curriculum.md')
                if os.path.exists(curriculum_path):
                    print(f"\n  ✓ Curriculum file: {curriculum_path}")
        else:
            print(f"  {base_dir}")
            if not os.path.exists(base_dir):
                print("  (Directory does not exist yet)")
        
        print("=" * 60)
        
        # Offer to open directory (macOS)
        if actual_dir and os.path.exists(actual_dir) and sys.platform == 'darwin':
            if get_yes_no("\nOpen output directory in Finder?", default=True):
                subprocess.run(['open', actual_dir])
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError executing command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
