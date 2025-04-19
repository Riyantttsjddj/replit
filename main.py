from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import threading
import os
import time
import re

from utils import extract_video_info, download_video, check_valid_url
from download_history import DownloadHistory

# Set default window size for development
Window.size = (400, 700)

class DownloadItem(BoxLayout):
    """Widget for displaying a downloaded video in the history"""
    title = StringProperty()
    thumbnail = StringProperty()
    date = StringProperty()
    file_path = StringProperty()
    
    def play_video(self):
        """Open the video with the default player"""
        try:
            from android.storage import primary_external_storage_path
            from android import mActivity
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            MediaStore = autoclass('android.provider.MediaStore')
            
            file = File(self.file_path)
            uri = Uri.fromFile(file)
            
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "video/*")
            mActivity.startActivity(intent)
        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f'Could not play video: {str(e)}'),
                         size_hint=(0.8, 0.3))
            popup.open()

class HomeScreen(Screen):
    """Main screen for entering URLs and downloading videos"""
    download_progress = NumericProperty(0)
    current_status = StringProperty("")
    quality_options = ListProperty(['Best', '1080p', '720p', '480p', '360p', 'Audio only'])
    
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.download_history = DownloadHistory()
        self.download_thread = None
        
    def check_url(self):
        """Validate the URL and get video information"""
        url = self.ids.url_input.text.strip()
        
        if not url:
            self.show_error('Please enter a YouTube URL')
            return
            
        if not check_valid_url(url):
            self.show_error('Invalid YouTube URL format')
            return
            
        self.ids.url_status.text = "Fetching video info..."
        
        # Start thread to fetch video info
        threading.Thread(target=self.fetch_video_info, args=(url,), daemon=True).start()
    
    def fetch_video_info(self, url):
        """Fetch video information in a separate thread"""
        try:
            video_info = extract_video_info(url)
            
            # Update UI in main thread
            Clock.schedule_once(lambda dt: self.update_video_info(video_info), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"), 0)
    
    def update_video_info(self, video_info):
        """Update UI with video information"""
        if not video_info:
            self.show_error('Could not fetch video information')
            return
            
        self.ids.video_title.text = video_info.get('title', 'Unknown title')
        self.ids.video_duration.text = f"Duration: {video_info.get('duration_string', 'Unknown')}"
        self.ids.url_status.text = "Video found! Select quality and download."
        self.ids.download_section.opacity = 1
        self.ids.download_section.disabled = False
        
    def download_video(self):
        """Start downloading the video with selected quality"""
        if self.download_thread and self.download_thread.is_alive():
            self.show_error('A download is already in progress')
            return
            
        url = self.ids.url_input.text.strip()
        quality = self.ids.quality_spinner.text
        
        # Convert UI quality option to format string for yt-dlp
        format_string = self.get_format_string(quality)
        
        # Reset progress
        self.download_progress = 0
        self.current_status = "Starting download..."
        self.ids.download_button.disabled = True
        
        # Start download in a thread
        self.download_thread = threading.Thread(
            target=self.download_thread_func,
            args=(url, format_string),
            daemon=True
        )
        self.download_thread.start()
        
        # Start progress updates
        Clock.schedule_interval(self.update_progress, 0.5)
    
    def get_format_string(self, quality):
        """Convert UI quality option to yt-dlp format string"""
        if quality == 'Best':
            return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif quality == '1080p':
            return 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
        elif quality == '720p':
            return 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
        elif quality == '480p':
            return 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
        elif quality == '360p':
            return 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'
        elif quality == 'Audio only':
            return 'bestaudio[ext=m4a]/bestaudio'
        return 'best'
    
    def download_thread_func(self, url, format_string):
        """Thread function to handle the download process"""
        try:
            # Get download directory (will be different on Android vs development)
            try:
                from android.storage import primary_external_storage_path
                download_dir = os.path.join(primary_external_storage_path(), 'Download')
            except ImportError:
                download_dir = os.path.expanduser('~/Downloads')
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
            
            # Progress callback
            def progress_hook(d):
                if d['status'] == 'downloading':
                    # Calculate progress percentage
                    if 'total_bytes' in d and d['total_bytes'] > 0:
                        percentage = d['downloaded_bytes'] / d['total_bytes'] * 100
                    elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                        percentage = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                    else:
                        percentage = 0
                    
                    # Store progress to be picked up by update_progress
                    self._progress = percentage
                    self._status = f"Downloading: {percentage:.1f}%"
                    
                elif d['status'] == 'finished':
                    self._status = "Download complete. Processing video..."
            
            # Perform download
            info, filepath = download_video(url, download_dir, format_string, progress_hook)
            
            if not info or not filepath:
                raise Exception("Download failed without error")
            
            # Add to download history
            self.download_history.add_download(
                title=info.get('title', 'Unknown'),
                url=url,
                filepath=filepath,
                thumbnail=info.get('thumbnail', '')
            )
            
            # Final update on main thread
            Clock.schedule_once(lambda dt: self.download_complete(filepath), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_error(str(e)), 0)
    
    def update_progress(self, dt):
        """Update progress bar (called by Clock)"""
        if hasattr(self, '_progress'):
            self.download_progress = self._progress
        
        if hasattr(self, '_status'):
            self.current_status = self._status
            
        # Check if download is still in progress
        if not self.download_thread or not self.download_thread.is_alive():
            return False  # Stop the interval
            
        return True  # Continue updating
    
    def download_complete(self, filepath):
        """Handle download completion"""
        self.download_progress = 100
        self.current_status = "Download complete!"
        self.ids.download_button.disabled = False
        
        # Show success popup
        popup = Popup(title='Success',
                     content=Label(text=f'Video downloaded to:\n{filepath}'),
                     size_hint=(0.8, 0.3))
        popup.open()
    
    def download_error(self, error_msg):
        """Handle download error"""
        self.current_status = f"Error: {error_msg}"
        self.ids.download_button.disabled = False
        self.show_error(f"Download failed: {error_msg}")
    
    def show_error(self, message):
        """Display error popup"""
        popup = Popup(title='Error',
                     content=Label(text=message),
                     size_hint=(0.8, 0.3))
        popup.open()
    
    def go_to_history(self):
        """Navigate to history screen"""
        self.manager.current = 'history'


class HistoryScreen(Screen):
    """Screen for showing download history"""
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.download_history = DownloadHistory()
    
    def on_enter(self):
        """Called when screen is entered - refresh history"""
        self.load_history()
    
    def load_history(self):
        """Load download history into the UI"""
        history_container = self.ids.history_container
        history_container.clear_widgets()
        
        downloads = self.download_history.get_downloads()
        
        if not downloads:
            history_container.add_widget(Label(text="No download history yet", 
                                              font_size=18,
                                              color=(0.7, 0.7, 0.7, 1)))
            return
        
        for download in downloads:
            item = DownloadItem(
                title=download['title'],
                thumbnail='',  # Not displaying thumbnails for simplicity
                date=download['date'],
                file_path=download['filepath']
            )
            history_container.add_widget(item)
    
    def clear_history(self):
        """Clear all download history"""
        confirm_popup = Popup(
            title='Confirm',
            content=BoxLayout(
                orientation='vertical',
                spacing=10,
                padding=10,
                children=[
                    Label(text='Clear all download history?'),
                    BoxLayout(
                        size_hint_y=None,
                        height=44,
                        spacing=10,
                        children=[
                            Button(
                                text='Cancel',
                                on_release=lambda x: confirm_popup.dismiss()
                            ),
                            Button(
                                text='Clear',
                                on_release=lambda x: self.perform_clear_history(confirm_popup)
                            )
                        ]
                    )
                ]
            ),
            size_hint=(0.8, 0.3)
        )
        confirm_popup.open()
    
    def perform_clear_history(self, popup):
        """Actually perform the history clearing"""
        self.download_history.clear_downloads()
        self.load_history()
        popup.dismiss()
    
    def go_to_home(self):
        """Navigate back to home screen"""
        self.manager.current = 'home'


class YTDownloaderApp(App):
    """Main application class"""
    def build(self):
        # Create screen manager and screens
        sm = ScreenManager()
        
        home_screen = HomeScreen(name='home')
        history_screen = HistoryScreen(name='history')
        
        sm.add_widget(home_screen)
        sm.add_widget(history_screen)
        
        return sm


if __name__ == '__main__':
    YTDownloaderApp().run()
