#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for ClipOrbit.
Creates a standalone Windows executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_icon():
    """Create a simple ICO file for the application"""
    try:
        from PIL import Image, ImageDraw

        # Create a 256x256 image with black background
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        # Create simple white circle outline
        circle_size = size - 40
        x = (size - circle_size) // 2
        y = (size - circle_size) // 2
        draw.ellipse([x, y, x + circle_size, y + circle_size], outline=(255, 255, 255, 255), width=8)

        # Add simple download arrow (white)
        arrow_size = 50
        cx, cy = size // 2, size // 2

        # Vertical line of arrow
        line_width = 8
        draw.rectangle([cx - line_width//2, cy - arrow_size//2, cx + line_width//2, cy + arrow_size//3], fill=(255, 255, 255, 255))

        # Arrow head
        arrow_head = [
            (cx - arrow_size//3, cy),
            (cx + arrow_size//3, cy),
            (cx, cy + arrow_size//3)
        ]
        draw.polygon(arrow_head, fill=(255, 255, 255, 255))

        # Save as ICO
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_path = Path('app_icon.ico')

        # Create multiple sizes for ICO
        icons = []
        for icon_size in icon_sizes:
            resized = img.resize(icon_size, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO file
        img.save(icon_path, format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
        print(f"[OK] Created app icon: {icon_path}")
        return str(icon_path)

    except ImportError:
        print("[WARN] Pillow not available, skipping icon creation")
        return None
    except Exception as e:
        print(f"[WARN] Failed to create icon: {e}")
        return None

def install_dependencies():
    """Install required dependencies"""
    print("[INFO] Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("[OK] Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        return False
    return True

def create_version_file():
    """Create a version file for PyInstaller"""
    try:
        from version_info import VERSION_INFO

        version_content = f'''# UTF-8

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'{VERSION_INFO["company"]}'),
          StringStruct(u'FileDescription', u'{VERSION_INFO["file_description"]}'),
          StringStruct(u'FileVersion', u'{VERSION_INFO["version"]}'),
          StringStruct(u'InternalName', u'{VERSION_INFO["internal_name"]}'),
          StringStruct(u'LegalCopyright', u'{VERSION_INFO["copyright"]}'),
          StringStruct(u'OriginalFilename', u'{VERSION_INFO["original_filename"]}'),
          StringStruct(u'ProductName', u'{VERSION_INFO["product"]}'),
          StringStruct(u'ProductVersion', u'{VERSION_INFO["version"]}'),
          StringStruct(u'Comments', u'{VERSION_INFO["description"]}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''

        with open('version_file.txt', 'w', encoding='utf-8') as f:
            f.write(version_content)

        print("[OK] Created version file")
        return 'version_file.txt'

    except Exception as e:
        print(f"[WARN] Failed to create version file: {e}")
        return None

def find_executable(name):
    """Find and resolve an executable path from PATH"""
    executable_path = shutil.which(name)
    if not executable_path:
        return None

    return os.path.realpath(executable_path)

def build_executable(icon_path=None):
    """Build the executable using PyInstaller"""
    print("[INFO] Building executable...")

    # Create version file
    version_file = create_version_file()
    ffmpeg_path = find_executable("ffmpeg")
    ffprobe_path = find_executable("ffprobe")

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # No console window
        '--name=ClipOrbit',             # Executable name
        '--distpath=dist',              # Output directory
        '--workpath=build',             # Work directory
        '--specpath=.',                 # Spec file location
        '--clean',                      # Clean cache
        '--noconfirm',                  # Overwrite without asking
    ]

    # Add icon if available
    if icon_path and os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])

    # Add version file if available
    if version_file and os.path.exists(version_file):
        cmd.extend(['--version-file', version_file])

    # Add more legitimate-looking options
    cmd.extend([
        '--add-data', 'requirements.txt;.',
        '--hidden-import=yt_dlp',
        '--hidden-import=yt_dlp.extractor',
        '--hidden-import=yt_dlp.postprocessor',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.filedialog',
    ])

    if icon_path and os.path.exists(icon_path):
        cmd.extend(['--add-data', f'{icon_path};.'])

    if ffmpeg_path and os.path.exists(ffmpeg_path):
        print(f"[OK] Bundling FFmpeg: {ffmpeg_path}")
        cmd.extend(['--add-binary', f'{ffmpeg_path};.'])
    else:
        print("[WARN] FFmpeg not found. High-resolution downloads may require users to install FFmpeg.")

    if ffprobe_path and os.path.exists(ffprobe_path):
        print(f"[OK] Bundling FFprobe: {ffprobe_path}")
        cmd.extend(['--add-binary', f'{ffprobe_path};.'])
    else:
        print("[WARN] FFprobe not found. Some media checks may be unavailable.")

    # Source file
    cmd.append('youtube_downloader.py')

    try:
        # Try to find PyInstaller in user scripts directory
        user_scripts = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python",
                                   f"Python{sys.version_info.major}{sys.version_info.minor}", "Scripts")
        pyinstaller_path = os.path.join(user_scripts, "pyinstaller.exe")

        if os.path.exists(pyinstaller_path):
            cmd[0] = pyinstaller_path

        subprocess.check_call(cmd)
        print("[OK] Executable built successfully!")

        # Check if file was created
        exe_path = Path('dist/ClipOrbit.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[INFO] Executable location: {exe_path}")
            print(f"[INFO] File size: {size_mb:.1f} MB")
            return True
        else:
            print("[ERROR] Executable not found in expected location")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False

def cleanup():
    """Clean up build artifacts"""
    print("[INFO] Cleaning up...")

    # Remove build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("[OK] Removed build directory")

    # Remove spec file
    spec_file = 'ClipOrbit.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print("[OK] Removed spec file")

    # Remove version file
    version_file = 'version_file.txt'
    if os.path.exists(version_file):
        os.remove(version_file)
        print("[OK] Removed version file")

    print("[OK] Cleanup complete")

def main():
    """Main build process"""
    print("ClipOrbit Build Script")
    print("=" * 40)

    # Check if source file exists
    if not os.path.exists('youtube_downloader.py'):
        print("[ERROR] youtube_downloader.py not found!")
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    # Create icon
    icon_path = create_icon()

    # Build executable
    if not build_executable(icon_path):
        return 1

    # Cleanup
    cleanup()

    print("\n[SUCCESS] Build completed successfully!")
    print("[INFO] Your executable is in the 'dist' folder")
    print("[INFO] You can now distribute ClipOrbit.exe")
    print("[INFO] The executable includes version metadata")

    return 0

if __name__ == '__main__':
    sys.exit(main())
