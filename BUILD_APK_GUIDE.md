# Panduan Membangun APK YouTube Downloader

## Prasyarat
- Docker terinstal di sistem Anda
- Koneksi internet aktif

## Langkah-langkah Membangun APK

### 1. Persiapan File

Pertama, pastikan semua file yang dibutuhkan sudah ada dalam proyek Anda:
- `main.py`: File aplikasi utama
- `main.kv`: File layout Kivy
- `utils.py`: File berisi fungsi utilitas
- `download_history.py`: File untuk mengelola riwayat unduhan
- `buildozer.spec`: File konfigurasi buildozer

### 2. Menggunakan Docker (Disarankan)

1. **Salin file Dockerfile** dari `attached_assets/Dockerfile` ke direktori utama proyek:
```
cp attached_assets/Dockerfile .
```

2. **Bangun image Docker** (proses ini akan memakan waktu cukup lama):
```
docker build -t ytdownloader-builder .
```

3. **Jalankan container untuk membangun APK**:
```
docker run --rm -v $(pwd):/app ytdownloader-builder
```

4. **Ambil file APK** dari folder `bin`:
Setelah proses build selesai, file APK akan berada di folder `./bin`.

### 3. Membangun APK secara Langsung (Linux)

Jika Anda menggunakan Linux, Anda dapat membangun APK secara langsung:

1. **Instal dependensi yang dibutuhkan**:
```
sudo apt-get update
sudo apt-get install -y python3-pip build-essential git python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
sudo apt-get install -y libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{tools,alsa} libzbar-dev
```

2. **Instal Buildozer**:
```
pip3 install --user --upgrade buildozer
```

3. **Jalankan proses build**:
```
buildozer android debug
```

Proses ini akan mengunduh dan menginstal Android SDK dan NDK, yang membutuhkan waktu dan ruang disk yang cukup besar.

## Catatan Penting

### Konfigurasi Buildozer

File `buildozer.spec` di proyek ini telah dikonfigurasi dengan pengaturan sebagai berikut:
- Android API level 33
- Mendukung arsitektur arm64-v8a dan armeabi-v7a
- Memerlukan izin INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, dan FOREGROUND_SERVICE
- Menggunakan Kivy 2.2.1 dan dependensi yang diperlukan

### Adaptasi untuk Android

Beberapa penyesuaian telah dilakukan agar aplikasi berfungsi dengan baik di Android:
- Menggunakan direktori penyimpanan yang sesuai di Android
- Menangani izin penyimpanan dengan benar
- Menyesuaikan antarmuka untuk layar sentuh

## Troubleshooting

### Masalah Umum:

1. **Kesalahan Kompilasi**:
   - Periksa log buildozer di .buildozer/logs/
   - Pastikan semua dependensi terinstal dengan benar

2. **Crash pada Peluncuran**:
   - Gunakan adb logcat untuk melihat log crash
   - Periksa izin Android yang dibutuhkan

3. **Masalah Unduhan**:
   - Pastikan aplikasi memiliki izin INTERNET dan akses penyimpanan
   - Periksa apakah URL YouTube valid

### Bantuan Lebih Lanjut:

Jika Anda mengalami masalah, periksa:
- Dokumentasi Kivy: https://kivy.org/doc/stable/
- Dokumentasi Buildozer: https://buildozer.readthedocs.io/
- Dokumentasi yt-dlp: https://github.com/yt-dlp/yt-dlp

## Langkah Selanjutnya

Setelah APK berhasil dibangun, Anda dapat menginstalnya di perangkat Android Anda.
Pastikan untuk mengaktifkan "Install dari sumber tidak dikenal" di pengaturan perangkat Anda.