import os
import json
from datetime import datetime

class DownloadHistory:
    """Kelas untuk mengelola riwayat unduhan
    
    Kelas ini menangani penyimpanan dan pengambilan data riwayat unduhan.
    Riwayat disimpan dalam format JSON dan mempertahankan informasi tentang
    video yang telah diunduh, termasuk judul, URL, jalur file, tanggal, dan ukuran.
    
    Attributes:
        data_dir (str): Direktori untuk menyimpan file riwayat
        history_file (str): Path lengkap ke file riwayat JSON
        downloads (list): Daftar entri riwayat unduhan
    """
    
    def __init__(self):
        """Inisialisasi objek riwayat unduhan
        
        Mendeteksi platform (Android atau desktop) dan menyiapkan
        direktori penyimpanan yang sesuai. Kemudian memuat riwayat
        unduhan dari disk jika tersedia.
        """
        # Coba dapatkan direktori data aplikasi
        try:
            # Path untuk Android
            from android.storage import app_storage_path
            self.data_dir = app_storage_path()
        except ImportError:
            # Fallback untuk platform non-Android
            self.data_dir = os.path.expanduser('~/.ytdownloader')
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
        
        self.history_file = os.path.join(self.data_dir, 'download_history.json')
        self.downloads = self._load_downloads()
    
    def _load_downloads(self):
        """Memuat riwayat unduhan dari file
        
        Returns:
            list: Daftar riwayat unduhan, kosong jika tidak ada file atau terjadi error
        """
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                # Validasi bahwa data adalah list
                if not isinstance(data, list):
                    print("Format file riwayat tidak valid, membuat riwayat baru")
                    return []
                return data
        except json.JSONDecodeError as e:
            print(f"Error parsing file riwayat: {e}")
            return []
        except Exception as e:
            print(f"Error memuat riwayat unduhan: {e}")
            return []
    
    def _save_downloads(self):
        """Menyimpan riwayat unduhan ke file
        
        Menulis data riwayat unduhan ke disk dalam format JSON.
        """
        try:
            # Pastikan direktori ada
            if not os.path.exists(os.path.dirname(self.history_file)):
                os.makedirs(os.path.dirname(self.history_file))
                
            with open(self.history_file, 'w') as f:
                json.dump(self.downloads, f, indent=2)
        except Exception as e:
            print(f"Error menyimpan riwayat unduhan: {e}")
    
    def add_download(self, title, url, filepath, thumbnail=''):
        """Menambahkan unduhan baru ke riwayat
        
        Args:
            title (str): Judul video
            url (str): URL video YouTube
            filepath (str): Path file lokal tempat video disimpan
            thumbnail (str, optional): URL thumbnail video
            
        Returns:
            dict: Entri unduhan yang baru ditambahkan
        """
        # Buat entri unduhan
        download = {
            'title': title,
            'url': url,
            'filepath': filepath,
            'thumbnail': thumbnail,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': self._get_file_size(filepath)
        }
        
        # Periksa apakah file ada
        if not os.path.exists(filepath):
            download['status'] = 'file_missing'
        else:
            download['status'] = 'completed'
        
        # Tambahkan ke daftar dan simpan
        self.downloads.insert(0, download)  # Tambahkan ke awal daftar
        self._save_downloads()
        
        return download
    
    def _get_file_size(self, filepath):
        """Mendapatkan ukuran file dalam format yang mudah dibaca manusia
        
        Args:
            filepath (str): Path ke file
            
        Returns:
            str: Ukuran file dengan unit (B, KB, MB, GB) yang sesuai
        """
        try:
            if not os.path.exists(filepath):
                return "File tidak ada"
                
            size_bytes = os.path.getsize(filepath)
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024 or unit == 'GB':
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024
                
            return "0 B"  # Fallback
        except Exception as e:
            print(f"Error mendapatkan ukuran file: {e}")
            return "Tidak diketahui"
    
    def get_downloads(self):
        """Mendapatkan daftar unduhan
        
        Juga memperbarui status file yang mungkin telah dipindahkan atau dihapus.
        
        Returns:
            list: Daftar semua entri unduhan
        """
        # Filter entri dengan file yang hilang jika mereka ditandai sebagai selesai
        valid_downloads = []
        
        for download in self.downloads:
            # Perbarui status jika file tidak ada lagi
            if download.get('status') == 'completed' and not os.path.exists(download.get('filepath', '')):
                download['status'] = 'file_missing'
            
            valid_downloads.append(download)
        
        return valid_downloads
    
    def clear_downloads(self):
        """Menghapus semua riwayat unduhan
        
        Menghapus semua entri dari riwayat dan menyimpan perubahan ke disk.
        """
        self.downloads = []
        self._save_downloads()
    
    def remove_download(self, filepath):
        """Menghapus unduhan tertentu dari riwayat
        
        Args:
            filepath (str): Path file dari unduhan yang akan dihapus
            
        Returns:
            bool: True jika item dihapus, False jika tidak ditemukan
        """
        old_count = len(self.downloads)
        self.downloads = [d for d in self.downloads if d.get('filepath') != filepath]
        
        # Simpan jika ada perubahan
        if old_count != len(self.downloads):
            self._save_downloads()
            return True
        return False
