import os
import re
import time
import subprocess
import json
import tempfile
from datetime import datetime

def check_valid_url(url):
    """Memeriksa apakah URL adalah URL YouTube yang valid
    
    Menggunakan ekspresi regex untuk memvalidasi format URL YouTube.
    Mendukung format URL YouTube standar seperti:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - https://youtube.com/v/VIDEOID
    
    Args:
        url (str): URL yang akan diperiksa
        
    Returns:
        bool: True jika URL valid, False jika tidak
    """
    if not url or not isinstance(url, str):
        return False
        
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    
    match = re.match(youtube_regex, url)
    return match is not None

def extract_video_info(url):
    """Mengekstrak informasi tentang video YouTube tanpa mengunduhnya
    
    Menggunakan yt-dlp untuk mendapatkan metadata video seperti judul,
    durasi, thumbnail dll.
    
    Args:
        url (str): URL YouTube yang valid
        
    Returns:
        dict: Dictionary berisi metadata video, atau None jika terjadi kesalahan
        
    Format dictionary yang dikembalikan:
    {
        'id': 'ID video YouTube',
        'title': 'Judul video',
        'duration': durasi_dalam_detik,
        'duration_string': 'durasi_dalam_format_mm:ss',
        'thumbnail': 'URL thumbnail',
        'uploader': 'Nama pengunggah',
        'upload_date': 'Tanggal unggah'
    }
    """
    if not check_valid_url(url):
        print("URL tidak valid")
        return None
        
    try:
        # Buat perintah untuk mendapatkan info video
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-playlist',
            url
        ]
        
        # Jalankan perintah
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        
        if not output.strip():
            print("Tidak ada output dari yt-dlp")
            return None
            
        # Parse output JSON
        info = json.loads(output)
        
        # Format durasi
        duration_secs = info.get('duration', 0)
        minutes, seconds = divmod(duration_secs, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            duration_string = f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            duration_string = f"{int(minutes)}:{int(seconds):02d}"
        
        # Ekstrak hanya yang kita butuhkan
        result = {
            'id': info.get('id', ''),
            'title': info.get('title', 'Judul Tidak Diketahui'),
            'duration': duration_secs,
            'duration_string': duration_string,
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader', 'Pengunggah Tidak Diketahui'),
            'upload_date': info.get('upload_date', '')
        }
        
        # Tambahkan format yang tersedia jika ada
        formats = info.get('formats', [])
        if formats:
            result['available_formats'] = [
                {
                    'format_id': f.get('format_id', ''),
                    'ext': f.get('ext', ''),
                    'width': f.get('width', 0),
                    'height': f.get('height', 0),
                    'resolution': f"{f.get('width', 0)}x{f.get('height', 0)}",
                    'filesize': f.get('filesize', 0)
                }
                for f in formats
            ]
        
        return result
    
    except subprocess.CalledProcessError as e:
        print(f"Error mendapatkan info video: {e}")
        # Tambahkan output stderr jika tersedia
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error output: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        # Output ditangani dalam blok try khusus
        return None
    except Exception as e:
        print(f"Error tidak terduga: {e}")
        return None

def download_video(url, download_dir, format_string, progress_hook=None):
    """Mengunduh video dari YouTube
    
    Args:
        url (str): URL YouTube yang valid
        download_dir (str): Direktori untuk menyimpan video yang diunduh
        format_string (str): Format string yt-dlp untuk kualitas video
        progress_hook (callable, optional): Fungsi callback untuk melaporkan kemajuan unduhan
        
    Returns:
        tuple: (info, filepath) - info adalah dictionary dengan metadata video, 
               filepath adalah path file video yang diunduh. 
               Jika terjadi error, keduanya akan None.
    """
    # Variabel untuk melacak progres dan proses
    downloaded_bytes = 0
    total_bytes = 0
    process = None
    filepath = None
    info = None
    
    try:
        # Pastikan direktori download ada
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        # Format perintah untuk unduhan
        cmd = [
            'yt-dlp',
            '--format', format_string,
            '--newline',
            '--progress',
            '--no-playlist',
            '--output', os.path.join(download_dir, '%(title)s.%(ext)s'),
            '--print-json',
            '--restrict-filenames',
            url
        ]
        
        # Mulai proses unduhan
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True, 
            bufsize=1,
            universal_newlines=True
        )
        
        # Jika stdout tidak tersedia, hentikan proses
        if process.stdout is None:
            raise Exception("Tidak dapat membaca output dari proses unduhan")
        
        # Baca output baris demi baris untuk melacak kemajuan
        for line in process.stdout:
            line = line.strip()
            
            # Parse output JSON (biasanya baris terakhir)
            if line.startswith('{') and line.endswith('}'):
                try:
                    info = json.loads(line)
                    filepath = info.get('requested_downloads', [{}])[0].get('filepath', '')
                    if not filepath and '_filename' in info:
                        filepath = info['_filename']
                except Exception as json_err:
                    print(f"Error parsing JSON: {json_err}")
                continue
            
            # Parse informasi kemajuan
            if '[download]' in line:
                # Coba ekstrak informasi kemajuan
                progress_match = re.search(r'(\d+\.\d+)% of (\d+\.\d+)(\w+)', line)
                if progress_match:
                    percent = float(progress_match.group(1))
                    size = float(progress_match.group(2))
                    unit = progress_match.group(3)
                    
                    # Konversi ukuran ke byte
                    if unit == 'KiB':
                        size *= 1024
                    elif unit == 'MiB':
                        size *= 1024 * 1024
                    elif unit == 'GiB':
                        size *= 1024 * 1024 * 1024
                    
                    total_bytes = size
                    downloaded_bytes = size * (percent / 100.0)
                    
                    # Panggil progress hook jika disediakan
                    if progress_hook:
                        progress_hook({
                            'status': 'downloading',
                            'downloaded_bytes': downloaded_bytes,
                            'total_bytes': total_bytes,
                            'filename': filepath
                        })
        
        # Tunggu proses selesai
        if process.wait() != 0:
            raise Exception(f"yt-dlp exited with code {process.returncode}")
        
        # Panggil progress hook dengan status selesai
        if progress_hook and filepath:
            progress_hook({
                'status': 'finished',
                'filename': filepath
            })
        
        # Jika kita tidak mendapatkan info dari output JSON, coba ekstrak info dasar
        if not info and filepath:
            base_filename = os.path.basename(filepath)
            info = {
                'title': os.path.splitext(base_filename)[0],
                'ext': os.path.splitext(base_filename)[1][1:],
                '_filename': filepath
            }
        
        # Verifikasi bahwa file benar-benar ada
        if filepath and not os.path.exists(filepath):
            raise Exception(f"File tidak ditemukan setelah unduhan: {filepath}")
            
        return info, filepath
    
    except Exception as e:
        print(f"Download error: {e}")
        # Hentikan proses jika masih berjalan
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except:
                pass  # Abaikan jika tidak dapat menghentikan proses
        return None, None
