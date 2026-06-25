# ClipOrbit

A sleek Windows YouTube video downloader with a dark, space-inspired interface and a simple resolution picker.

ClipOrbit is built for people who want a straightforward MP4 downloader without digging through command-line options. Paste a YouTube URL, choose one of the available resolutions, and download.

## Features

- Download YouTube videos as MP4 files
- Detect available resolutions before downloading
- Choose from available qualities like 2160p, 1440p, 1080p, 720p, and lower when YouTube provides them
- Merge high-resolution video with audio using bundled FFmpeg in release builds
- Pick a custom output folder
- Build a standalone Windows EXE with PyInstaller

demo:



https://github.com/user-attachments/assets/f8233176-41c9-4595-a269-7e2eeb095e3e





## Download

For normal users, download `ClipOrbit.exe` from the repository releases page once a release is published.

## Run From Source

```powershell
git clone https://github.com/parthisapro69420-prog/cliporbit-youtube-downloader.git
cd cliporbit-youtube-downloader
python -m pip install -r requirements.txt
python youtube_downloader.py
```

## Build The Standalone EXE

Install FFmpeg first if you want high-resolution release builds to work on machines that do not already have FFmpeg installed. The build script bundles `ffmpeg.exe` and `ffprobe.exe` when they are available on `PATH`.

```powershell
python -m pip install -r requirements.txt
python build.py
```

The standalone executable is created at:

```text
dist/ClipOrbit.exe
```

## Project Structure

```text
cliporbit-youtube-downloader/
├── youtube_downloader.py
├── build.py
├── build.bat
├── version_info.py
├── requirements.txt
├── app_icon.ico
├── README.md
├── LICENSE
├── NOTICE.md
└── .gitignore
```

## Important Notes

- ClipOrbit is intended for personal use.
- Only download content you own, have permission to download, or are legally allowed to save.
- Respect YouTube's Terms of Service and copyright law.

## Attribution

ClipOrbit is derived from VoidGrab by Adarsh.

Original project: https://github.com/itsjustadarsh/VoidGrab

See `NOTICE.md` for third-party license notes.
