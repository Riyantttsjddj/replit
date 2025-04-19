# Panduan Membangun APK dengan Layanan Online

Jika Anda tidak memiliki lingkungan lokal yang mendukung untuk build Android, Anda dapat menggunakan layanan build online sebagai alternatif. Berikut adalah beberapa pilihan dan panduan penggunaannya.

## 1. Menggunakan Codemagic.io

[Codemagic](https://codemagic.io/) adalah CI/CD platform yang dibuat khusus untuk aplikasi mobile termasuk Flutter, React Native, Ionic, Cordova, dan native Android/iOS. Platform ini memiliki free tier yang dapat digunakan.

### Langkah-langkah:

1. **Daftar di Codemagic**:
   - Buat akun di Codemagic.io, Anda dapat mendaftar dengan GitHub account.

2. **Siapkan Repository**:
   - Upload kode Anda ke GitHub, GitLab, atau Bitbucket.
   - Pastikan sudah memiliki `buildozer.spec` di root directory.

3. **Tambahkan Proyek ke Codemagic**:
   - Di dashboard Codemagic, klik "Add application".
   - Pilih repository Anda.

4. **Konfigurasi Build**:
   - Pilih "Android" sebagai platform.
   - Tambahkan script berikut di bagian "Pre-build script":
     ```bash
     pip3 install --upgrade pip
     pip3 install cython==0.29.33
     pip3 install buildozer
     sudo apt-get update
     sudo apt-get install -y git zip unzip openjdk-11-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
     sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
     sudo apt-get install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
     sudo apt-get install -y python3-setuptools build-essential libsqlite3-dev
     ```
   - Di bagian "Build script", tambahkan:
     ```bash
     buildozer android debug
     ```

5. **Mulai Build**:
   - Klik "Start Build".
   - Proses build akan memakan waktu 20-30 menit.

6. **Download APK**:
   - Setelah build selesai, Anda dapat mendownload APK dari halaman build.

## 2. Menggunakan GitHub Actions (Disarankan)

Metode ini menggunakan GitHub sebagai platform dan memanfaatkan GitHub Actions sebagai sistem build. File konfigurasi sudah disediakan di repository ini.

### Langkah-langkah:

1. **Buat Repository GitHub**:
   - Buat repository baru di GitHub.
   - Upload seluruh code dari Replit ke repository tersebut.

2. **Aktifkan GitHub Actions**:
   - Pastikan folder `.github/workflows` dengan file `build_apk.yml` ada di repository.
   - GitHub akan otomatis mendeteksi dan menjalankan workflow ketika Anda push code.

3. **Memulai Build**:
   - Bisa dipicu otomatis dengan push ke branch `main`.
   - Atau bisa dijalankan manual dari tab "Actions" di repository GitHub.

4. **Download APK**:
   - Setelah workflow selesai, klik build yang sudah jadi.
   - Di halaman build detail, cari bagian "Artifacts".
   - Download file `ytdownloader-apk.zip` yang berisi APK.

## 3. Menggunakan Appetize.io untuk Testing

[Appetize.io](https://appetize.io/) memungkinkan Anda untuk menjalankan aplikasi Android di browser tanpa harus menginstal di perangkat. Ini berguna untuk testing aplikasi.

### Langkah-langkah:

1. **Build APK** terlebih dahulu menggunakan metode di atas.
2. **Daftar di Appetize.io**.
3. **Upload APK** ke Appetize.io.
4. **Dapatkan link public** untuk aplikasi Anda.
5. **Bagikan link** kepada siapapun yang ingin mencoba aplikasi tanpa menginstal.

## Catatan Penting

- Semua layanan di atas memiliki batasan pada free tier.
- Proses build Android membutuhkan waktu yang cukup lama (20-30 menit).
- Jika Anda memiliki akses ke komputer dengan Linux atau Mac, build secara lokal mungkin lebih cepat.

## Troubleshooting

### Masalah Umum di GitHub Actions:

1. **Build Gagal**:
   - Cek log untuk melihat error spesifik.
   - Pastikan semua dependensi di `buildozer.spec` benar.

2. **APK Tidak Diproduksi**:
   - Pastikan konfigurasi `build_apk.yml` benar.
   - Cek apakah path artifact (`bin/*.apk`) sudah benar.

3. **Build Timeout**:
   - GitHub Actions memiliki batas waktu 6 jam, yang seharusnya cukup untuk build Android.
   - Jika timeout, coba sederhanakan `buildozer.spec` (misalnya, targetkan hanya satu arsitektur).

Untuk bantuan lebih lanjut, lihat:
- [Dokumentasi GitHub Actions](https://docs.github.com/en/actions)
- [Dokumentasi Buildozer](https://buildozer.readthedocs.io/)
- [Forum Kivy](https://github.com/kivy/kivy/discussions)