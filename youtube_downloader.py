import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import subprocess
import sys
import shutil
from tkinter import Canvas
import base64
from io import BytesIO

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def bundled_ffmpeg_dir():
    ffmpeg_path = resource_path("ffmpeg.exe")
    ffprobe_path = resource_path("ffprobe.exe")
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        return os.path.dirname(ffmpeg_path)
    return None

class ResolutionDialog:
    def __init__(self, parent, colors, title, formats):
        self.parent = parent
        self.colors = colors
        self.formats = formats
        self.selected_format = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Choose Resolution")
        self.dialog.configure(bg=self.colors['bg'])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        container = tk.Frame(self.dialog, bg=self.colors['bg'], padx=24, pady=22)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        tk.Label(container, text="Choose Resolution",
                font=("Segoe UI", 18, "bold"),
                fg=self.colors['text'], bg=self.colors['bg']).grid(row=0, column=0, sticky="w")

        tk.Label(container, text=title,
                font=("Segoe UI", 10),
                fg=self.colors['text_secondary'], bg=self.colors['bg'],
                wraplength=420, justify="left").grid(row=1, column=0, sticky="ew", pady=(6, 18))

        self.resolution_var = tk.StringVar()
        self.resolution_menu = ttk.Combobox(container, textvariable=self.resolution_var,
                                           values=[item['label'] for item in self.formats],
                                           state="readonly", width=48)
        self.resolution_menu.grid(row=2, column=0, sticky="ew")
        self.resolution_menu.current(0)

        button_frame = tk.Frame(container, bg=self.colors['bg'])
        button_frame.grid(row=3, column=0, sticky="e", pady=(22, 0))

        tk.Button(button_frame, text="Cancel", font=("Segoe UI", 10),
                  bg=self.colors['secondary_bg'], fg=self.colors['text'],
                  relief="flat", bd=0, padx=16, pady=7,
                  command=self.cancel).grid(row=0, column=0, padx=(0, 10))

        tk.Button(button_frame, text="Download", font=("Segoe UI", 10, "bold"),
                  bg=self.colors['accent'], fg=self.colors['bg'],
                  relief="flat", bd=0, padx=18, pady=7,
                  command=self.confirm).grid(row=0, column=1)

        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.center()

    def center(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def confirm(self):
        selected_label = self.resolution_var.get()
        for item in self.formats:
            if item['label'] == selected_label:
                self.selected_format = item
                break
        self.dialog.destroy()

    def cancel(self):
        self.selected_format = None
        self.dialog.destroy()

    def show(self):
        self.parent.wait_window(self.dialog)
        return self.selected_format

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("ClipOrbit - YouTube Video Downloader")
        self.root.geometry("800x700")
        self.root.configure(bg='#1a1a1a')

        # Set custom icon
        try:
            self.root.iconbitmap(resource_path("app_icon.ico"))
        except:
            pass  # Fallback if icon not found

        # Variables
        self.output_folder = os.path.join(os.getcwd(), "output")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)


        # Colors - Black bg and White text
        self.colors = {
            'bg': '#000000',
            'secondary_bg': '#1a1a1a',
            'accent': '#ffffff',
            'accent_hover': '#cccccc',
            'text': '#ffffff',
            'text_secondary': '#aaaaaa',
            'success': '#ffffff',
            'error': '#ffffff',
            'border': '#333333'
        }

        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        # Configure root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)

        # Using default title bar with custom icon

        # Content frame
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        # Give minimal weight to header, form elements, and download button
        content_frame.rowconfigure(0, weight=0)  # header
        content_frame.rowconfigure(1, weight=0)  # url
        content_frame.rowconfigure(2, weight=0)  # output
        content_frame.rowconfigure(3, weight=0)  # download button

        # App icon and title
        header_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))


        title_label = tk.Label(header_frame, text="ClipOrbit",
                              font=("Segoe UI", 24, "bold"),
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(pady=(10, 2))

        subtitle_label = tk.Label(header_frame, text="YouTube Video Downloader",
                                font=("Segoe UI", 11),
                                fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(pady=(0, 5))

        # URL input section
        url_frame = tk.Frame(content_frame, bg=self.colors['secondary_bg'], relief="solid", bd=1)
        url_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)

        tk.Label(url_frame, text="URL:", font=("Segoe UI", 11, "bold"),
                fg=self.colors['text'], bg=self.colors['secondary_bg']).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, font=("Segoe UI", 11),
                                 bg=self.colors['bg'], fg=self.colors['text'],
                                 relief="flat", bd=6, insertbackground=self.colors['text'])
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=15)


        # Output folder section
        folder_frame = tk.Frame(content_frame, bg=self.colors['secondary_bg'], relief="solid", bd=1)
        folder_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)

        tk.Label(folder_frame, text="Output:", font=("Segoe UI", 11, "bold"),
                fg=self.colors['text'], bg=self.colors['secondary_bg']).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        folder_inner_frame = tk.Frame(folder_frame, bg=self.colors['secondary_bg'])
        folder_inner_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=15)
        folder_inner_frame.columnconfigure(0, weight=1)

        self.folder_var = tk.StringVar(value=self.output_folder)
        self.folder_entry = tk.Entry(folder_inner_frame, textvariable=self.folder_var, font=("Segoe UI", 10),
                                    bg=self.colors['bg'], fg=self.colors['text_secondary'],
                                    relief="flat", bd=5, state="readonly")
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.create_browse_button(folder_inner_frame)

        # Download button and progress
        download_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        download_frame.grid(row=3, column=0, sticky="ew", pady=(15, 10), ipady=5)
        download_frame.columnconfigure(0, weight=1)

        self.create_download_button(download_frame)

        # Progress bar
        self.progress_frame = tk.Frame(download_frame, bg=self.colors['bg'])
        self.progress_frame.grid(row=1, column=0, sticky="ew", pady=(15, 0))
        self.progress_frame.columnconfigure(0, weight=1)

        self.progress = tk.Canvas(self.progress_frame, height=6, bg=self.colors['border'], highlightthickness=0)
        self.progress.grid(row=0, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = tk.Label(self.progress_frame, textvariable=self.status_var,
                                   font=("Segoe UI", 10), fg=self.colors['text_secondary'],
                                   bg=self.colors['bg'])
        self.status_label.grid(row=1, column=0, pady=(5, 0))


    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")




    def create_browse_button(self, parent):
        browse_btn = tk.Button(parent, text="Browse", font=("Segoe UI", 10),
                              bg=self.colors['accent'], fg=self.colors['bg'],
                              relief="flat", bd=0, padx=10, pady=5,
                              command=self.browse_folder)
        browse_btn.grid(row=0, column=1)

    def create_download_button(self, parent):
        self.download_btn = tk.Button(parent, text="Download MP4", font=("Segoe UI", 13, "bold"),
                                     bg=self.colors['accent'], fg=self.colors['bg'],
                                     relief="flat", bd=0, padx=35, pady=12,
                                     command=self.start_download)
        self.download_btn.grid(row=0, column=0, pady=10, sticky="")

        # Hover effects
        def on_enter(e):
            self.download_btn.config(bg=self.colors['accent_hover'])

        def on_leave(e):
            self.download_btn.config(bg=self.colors['accent'])

        self.download_btn.bind("<Enter>", on_enter)
        self.download_btn.bind("<Leave>", on_leave)


    def close_app(self):
        self.root.quit()

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.folder_var.set(folder)


    def check_dependencies(self):
        try:
            import yt_dlp
            return True
        except ImportError:
            return False


    def install_ytdlp(self):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            return True
        except subprocess.CalledProcessError:
            return False

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        if not self.check_dependencies():
            if not self.install_ytdlp():
                return

        self.download_btn.config(state="disabled")
        self.start_progress_animation()
        self.status_var.set("Checking available resolutions...")

        thread = threading.Thread(target=self.prepare_download, args=(url,))
        thread.daemon = True
        thread.start()

    def prepare_download(self, url):
        try:
            import yt_dlp

            ydl_opts = {
                'quiet': True,
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            available_formats = self.get_available_formats(info)
            if not available_formats:
                self.root.after(0, self.download_complete, False, "No MP4 resolutions with audio were found for this video.")
                return

            self.root.after(0, self.show_resolution_picker, url, info, available_formats)

        except Exception as e:
            self.root.after(0, self.download_complete, False, str(e))

    def get_available_formats(self, info):
        formats_by_height = {}

        for item in info.get('formats', []):
            height = item.get('height')
            format_id = item.get('format_id')
            extension = item.get('ext')
            video_codec = item.get('vcodec')
            audio_codec = item.get('acodec')

            if not height or not format_id:
                continue

            if extension != 'mp4' or video_codec == 'none':
                continue

            existing = formats_by_height.get(height)
            if not existing or self.get_format_score(item) > self.get_format_score(existing):
                formats_by_height[height] = item

        available_formats = []
        for height in sorted(formats_by_height.keys(), reverse=True):
            item = formats_by_height[height]
            filesize = item.get('filesize') or item.get('filesize_approx')
            filesize_text = self.format_filesize(filesize)
            note = item.get('format_note') or f"{height}p"
            fps = item.get('fps')
            fps_text = f" {fps}fps" if fps else ""
            size_text = f" - {filesize_text}" if filesize_text else ""
            needs_audio_merge = item.get('acodec') == 'none'
            audio_text = " + audio" if needs_audio_merge else ""
            format_id = item.get('format_id')

            available_formats.append({
                'format_id': f"{format_id}+bestaudio[ext=m4a]/bestaudio" if needs_audio_merge else format_id,
                'height': height,
                'label': f"{height}p{fps_text} MP4 ({note}{audio_text}){size_text}",
                'needs_audio_merge': needs_audio_merge,
            })

        return available_formats

    def get_format_score(self, item):
        filesize = item.get('filesize') or item.get('filesize_approx') or 0
        tbr = item.get('tbr') or 0
        width = item.get('width') or 0
        return (filesize, tbr, width)

    def format_filesize(self, filesize):
        if not filesize:
            return ""

        size = float(filesize)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}"
            size /= 1024

        return ""

    def show_resolution_picker(self, url, info, available_formats):
        self.stop_progress_animation()
        self.status_var.set("Choose a resolution")

        title = info.get('title', 'Unknown video')
        dialog = ResolutionDialog(self.root, self.colors, title, available_formats)
        selected_format = dialog.show()

        if not selected_format:
            self.download_btn.config(state="normal")
            self.status_var.set("Ready to download")
            return

        self.start_progress_animation()
        self.status_var.set(f"Downloading {selected_format['height']}p MP4...")

        thread = threading.Thread(target=self.download_video, args=(url, selected_format))
        thread.daemon = True
        thread.start()

    def download_video(self, url, selected_format):
        try:
            import yt_dlp

            ffmpeg_location = bundled_ffmpeg_dir()

            if selected_format.get('needs_audio_merge') and not ffmpeg_location and not shutil.which("ffmpeg"):
                self.root.after(0, self.download_complete, False, "This resolution needs FFmpeg to merge video and audio. Install FFmpeg or choose a lower combined MP4 resolution.")
                return

            output_path = os.path.join(self.output_folder, "%(title)s.%(ext)s")
            ydl_opts = {
                'format': selected_format['format_id'],
                'outtmpl': output_path,
                'noplaylist': True,
            }

            if ffmpeg_location:
                ydl_opts['ffmpeg_location'] = ffmpeg_location

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')

                ydl.download([url])

                self.root.after(0, self.download_complete, True, f"Downloaded: {title} ({selected_format['height']}p MP4)")

        except Exception as e:
            self.root.after(0, self.download_complete, False, str(e))

    def start_progress_animation(self):
        self.progress_active = True
        self.animate_progress()

    def animate_progress(self):
        if not hasattr(self, 'progress_active') or not self.progress_active:
            return

        width = self.progress.winfo_width()
        if width <= 1:
            self.root.after(50, self.animate_progress)
            return

        self.progress.delete("all")

        # Create animated progress bar
        if not hasattr(self, 'progress_x'):
            self.progress_x = 0

        bar_width = 100
        if self.progress_x + bar_width > width:
            self.progress_x = -bar_width

        self.progress.create_rectangle(self.progress_x, 0, self.progress_x + bar_width, 6,
                                     fill=self.colors['accent'], outline='')

        self.progress_x += 3
        self.root.after(50, self.animate_progress)

    def stop_progress_animation(self):
        self.progress_active = False
        self.progress.delete("all")

    def download_complete(self, success, message):
        self.stop_progress_animation()
        self.download_btn.config(state="normal")

        if success:
            self.status_var.set("✅ Download completed!")

            # Show success in progress bar
            width = self.progress.winfo_width()
            self.progress.create_rectangle(0, 0, width, 6, fill=self.colors['success'], outline='')

            messagebox.showinfo("Success", f"Download completed!\n{message}")
        else:
            self.status_var.set("❌ Download failed!")

            # Show error in progress bar
            width = self.progress.winfo_width()
            self.progress.create_rectangle(0, 0, width, 6, fill=self.colors['error'], outline='')

            messagebox.showerror("Error", f"Download failed:\n{message}")

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
