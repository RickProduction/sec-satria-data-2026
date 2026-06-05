import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from ml_pipeline import predict_trauma

app = Flask(__name__)
app.secret_key = "satria_data_sec_2026"

# Konfigurasi Database MySQL (Ganti root dan password sesuai XAMPP/MySQL kamu)
# Format: mysql+pymysql://username:password@localhost/nama_database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_spkk_trauma'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Inisiasi Database
db = SQLAlchemy(app)

# --- SKEMA DATABASE ---
class RekamMedis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pasien = db.Column(db.String(100), nullable=False)
    file_ct_scan = db.Column(db.String(255), nullable=False)
    any_injury = db.Column(db.Integer, default=0) # 1 jika ada cedera, 0 jika sehat
    confidence = db.Column(db.Float, default=0.0)
    liver_status = db.Column(db.String(50))
    kidney_status = db.Column(db.String(50))
    spleen_status = db.Column(db.String(50))
    bowel_status = db.Column(db.String(50))

# Buat tabel otomatis jika belum ada saat aplikasi dijalankan
with app.app_context():
    db.create_all()

# --- ROUTING FRONTEND & LOGIKA ---

@app.route('/')
def dashboard():
    # Menampilkan semua pasien, diurutkan: yang cedera (any_injury=1) tampil paling atas
    pasien_list = RekamMedis.query.order_by(RekamMedis.any_injury.desc(), RekamMedis.confidence.desc()).all()
    return render_template('index.html', pasien_list=pasien_list)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file_ct' not in request.files:
        flash('Tidak ada file yang diunggah')
        return redirect(request.url)
    
    file = request.files['file_ct']
    nama_pasien = request.form.get('nama_pasien')
    
    if file.filename == '':
        flash('File belum dipilih')
        return redirect(url_for('dashboard'))
    
    if file:
        # 1. Simpan gambar dari Frontend
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Pastikan folder uploads ada
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        # 2. Panggil Model Machine Learning (Integrasi)
        hasil_prediksi = predict_trauma(filepath)
        
        # 3. Simpan ke Database MySQL
        rekam_medis_baru = RekamMedis(
            nama_pasien=nama_pasien,
            file_ct_scan=filename,
            any_injury=hasil_prediksi['any_injury'],
            confidence=hasil_prediksi['confidence'],
            liver_status=hasil_prediksi['liver_status'],
            kidney_status=hasil_prediksi['kidney_status'],
            spleen_status=hasil_prediksi['spleen_status'],
            bowel_status=hasil_prediksi['bowel_status']
        )
        db.session.add(rekam_medis_baru)
        db.session.commit()
        
        # Redirect ke halaman detail pasien tersebut
        return redirect(url_for('detail', id=rekam_medis_baru.id))

@app.route('/pasien/<int:id>')
def detail(id):
    # Mengambil data satu pasien untuk ditampilkan visualisasi multi-organnya
    pasien = RekamMedis.query.get_or_404(id)
    return render_template('detail.html', pasien=pasien)

if __name__ == '__main__':
    app.run(debug=True, port=5000)