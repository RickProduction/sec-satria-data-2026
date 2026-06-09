readme_content = """# Sistem Pendukung Keputusan Klinis (SPKK) Deteksi Trauma Abdomen Multi-Organ

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