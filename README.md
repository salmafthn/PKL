# Proyek Text-to-SQL dengan Streamlit, MySQL, dan Ollama

Proyek ini dipaketkan menggunakan Docker dan Docker Compose untuk memastikan dapat berjalan di lingkungan manapun dengan mudah.

Install **Docker Dekstop** terlebih dahulu lalu pastikan sudah berjalan di komputer.

Langkah langkah menggunakan aplikasi ini:
1.  **Ekstrak Folder Proyek**: Ekstrak file ZIP proyek ini ke sebuah folder di komputer Anda.
2.  **Buka terminal lalu Masuk ke Folder Proyek**: Gunakan perintah `cd` (change directory) untuk masuk ke folder yang baru saja Anda ekstrak. Contoh:
    ```bash
    cd C:\Users\NamaAnda\Downloads\proyek-streamlit-sql
    ```
4.  **Jalankan Docker Compose**: Ketik perintah di bawah ini lalu tekan Enter. Perintah ini akan secara otomatis mengunduh, membangun, dan menjalankan semua komponen.
    **Proses ini akan memakan waktu cukup lama saat pertama kali dijalankan.**
    ```
    docker-compose up --build
    ```
    Lalu biarkan terminal ini tetap terbuka.
5.  **Unduh Model AI (Hanya Sekali)**: Setelah log di terminal pertama sudah jalan, buka **terminal kedua** (jangan tutup terminal yang pertama). Ketik command di bawah ini untuk mengunduh model AI `mistral`.
    **Anda hanya perlu melakukan ini satu kali saja.**
    ```
    docker exec -it ollama_service ollama run mistral
    ```
    Tunggu hingga proses unduh dan verifikasi selesai di terminal kedua ini. Setelah selesai, Anda bisa menutup terminal kedua.
6.  **Buka Aplikasi**: Buka browser web Anda (seperti Chrome atau Firefox) dan kunjungi alamat berikut:
    [**http://localhost:8501**](http://localhost:8501)

Aplikasi Anda kini siap digunakan!

## Menghentikan Aplikasi
Untuk mematikan semua layanan:

1.  Kembali ke **terminal pertama** (yang menjalankan `docker-compose up`).
2.  Tekan tombol `Ctrl` + `C` secara bersamaan.
3.  Tunggu beberapa saat hingga semua layanan berhenti.