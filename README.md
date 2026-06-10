# Sistem Pendukung Keputusan Klinis (SPKK) Deteksi Trauma Abdomen Multi-Organ

SPKK Deteksi Trauma Abdomen Multi-Organ adalah sebuah platform digital berbasis Kecerdasan Buatan (AI) yang dirancang khusus untuk membantu tenaga medis di Instalasi Gawat Darurat (IGD) dalam melakukan triase pasien cedera perut. Sistem ini secara otomatis mampu mendeteksi indikasi trauma serta tingkat urgensi penanganan pada 4 organ target sekaligus: **Hati (Liver)**, **Ginjal (Kidney)**, **Limpa (Spleen)**, dan **Usus (Bowel)** dari hasil citra CT Scan abdomen berformat DICOM (`.dcm`).

Proyek ini dikembangkan menggunakan arsitektur terpisah (*Decoupled Architecture*) untuk menjamin performa komputasi tingkat tinggi, skalabilitas yang baik, serta antarmuka pengguna yang responsif dalam kondisi kritis medis. Aplikasi ini dikompilasi untuk kompetisi **Satria Data 2026 (Smart Elites Competition - SEC)**.

---

## 🚀 Fitur Utama Sistem

1. **Triase Pasien Otomatis (Smart Triage Queue):** Sistem antrean pintar di mana pasien dengan indikasi cedera parah otomatis diurutkan ke baris paling atas dengan indikator visual kritis (warna merah) untuk prioritas penanganan IGD.
2. **Prediksi Klasifikasi Multi-Output:** Menggunakan satu model *Machine Learning* tunggal yang mampu memprediksi probabilitas kondisi kesehatan dari 4 organ internal utama secara simultan.
3. **Prapemrosesan Medis Standar (Windowing HU):** Mengonversi nilai piksel mentah DICOM menjadi *Hounsfield Unit* (HU) dengan rentang jaringan lunak abdomen (-50 hingga 150 HU) guna memperjelas visualisasi visual organ radiologi.
4. **Ekstraksi Fitur Tekstur Statistik:** Reduksi dimensi citra berukuran besar menjadi 5 komponen statistik utama (*Mean, Standard Deviation, Variance, Skewness, Kurtosis*) sehingga komputasi model sangat ringan dan dapat dieksekusi tanpa GPU spesifikasi tinggi.
5. **Panel Hasil Terperinci (Multi-Organ Dashboard):** Visualisasi indikator kesehatan masing-masing organ menggunakan pendekatan *progress bar* dinamis yang intuitif sebagai alat bantu opini kedua (*second opinion*) bagi dokter.

---

## 🛠️ Tech Stack & Arsitektur

Sistem ini sepenuhnya dibangun secara lokal tanpa ketergantungan pada CDN eksternal guna mengoptimalkan kecepatan akses dan privasi data medis:

### Frontend (Client Side)
* **Framework:** React.js (Build system via Vite)
* **Styling:** Tailwind CSS (Instalasi lokal terkompresi)
* **HTTP Client:** Axios (Komunikasi data asinkron dengan REST API)
* **Routing:** React Router DOM (Navigasi halaman instan tanpa *reload*)

### Backend (Server Side / REST API)
* **Framework:** Python Flask
* **Security Cross-Origin:** Flask-CORS (Mengizinkan jembatan komunikasi lintas *port*)
* **Database ORM:** Flask-SQLAlchemy & PyMySQL
* **ML Engine:** Scikit-Learn (v1.6.1), Joblib, NumPy, SciPy
* **Medical Image Processor:** PyDicom & OpenCV Python (`cv2`)

### Database Layer
* **DBMS:** MySQL (XAMPP / Laragon)

---

## 🗃️ Skema Database MySQL

Sistem mengimplementasikan tabel tunggal teroptimasi bernama `riwayat_triase` untuk menyimpan catatan histori deteksi tanpa kehilangan data saat server dimatikan.

```sql
CREATE TABLE riwayat_triase (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_pasien VARCHAR(100) NOT NULL,
    file_dicom VARCHAR(255) NOT NULL,
    status_kritis TINYINT(1) DEFAULT 0,
    probabilitas_max FLOAT DEFAULT 0.0,
    hati_status VARCHAR(20),
    hati_conf FLOAT,
    ginjal_status VARCHAR(20),
    ginjal_conf FLOAT,
    limpa_status VARCHAR(20),
    limpa_conf FLOAT,
    usus_status VARCHAR(20),
    usus_conf FLOAT,
    waktu_periksa DATETIME DEFAULT CURRENT_TIMESTAMP
);

## 📦 Panduan Instalasi & Pengoperasian

Pastikan komputer Anda telah terpasang **Node.js**, **Python 3.10+**, dan **XAMPP/MySQL Control Panel**.

### 1. Persiapan Database
1. Buka XAMPP, aktifkan modul **Apache** dan **MySQL**.
2. Masuk ke phpMyAdmin (`http://localhost/phpmyadmin`).
3. Buat database baru dengan nama `db_spkk_trauma`.

### 2. Konfigurasi Backend (Flask REST API)
1. Buka terminal baru dan masuk ke folder backend:
   ```bash
   cd backend

Buat dan aktifkan *Virtual Environment* (`.venv`):

```bash
# Windows (PowerShell / CMD)
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS / Git Bash Windows
python3 -m venv .venv
source .venv/bin/activate