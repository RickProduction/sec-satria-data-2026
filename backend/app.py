import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from ml_pipeline import predict_trauma

app = Flask(__name__)

# Wajib untuk mengizinkan React (biasanya jalan di port 5173/3000) mengakses Flask
CORS(app)

# Konfigurasi Database (Ganti sesuai setting MySQL kamu)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/db_abdominaltrauma'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Lokasi penyimpanan gambar sementara
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

db = SQLAlchemy(app)

# MODEL DATABASE (Sesuai dengan tabel riwayat_triase)
class RiwayatTriase(db.Model):
    __tablename__ = 'riwayat_triase'
    id = db.Column(db.Integer, primary_key=True)
    nama_pasien = db.Column(db.String(100), nullable=False)
    file_dicom = db.Column(db.String(255), nullable=False)
    status_kritis = db.Column(db.Integer, default=0)
    probabilitas_max = db.Column(db.Float, default=0.0)
    
    hati_status = db.Column(db.String(20))
    hati_conf = db.Column(db.Float)
    ginjal_status = db.Column(db.String(20))
    ginjal_conf = db.Column(db.Float)
    limpa_status = db.Column(db.String(20))
    limpa_conf = db.Column(db.Float)
    usus_status = db.Column(db.String(20))
    usus_conf = db.Column(db.Float)
    # waktu_periksa otomatis diatur oleh MySQL

# Inisialisasi DB dan Folder
with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==========================================
# ENDPOINT API UNTUK REACT
# ==========================================

# 1. API: Mengambil semua data antrean pasien
@app.route('/api/pasien', methods=['GET'])
def get_semua_pasien():
    # Diurutkan berdasarkan yang paling kritis dulu (Triase)
    pasien_list = RiwayatTriase.query.order_by(
        RiwayatTriase.status_kritis.desc(), 
        RiwayatTriase.probabilitas_max.desc()
    ).all()
    
    data = []
    for p in pasien_list:
        data.append({
            "id": p.id,
            "nama_pasien": p.nama_pasien,
            "status_kritis": p.status_kritis,
            "probabilitas_max": p.probabilitas_max
        })
    
    return jsonify({"status": "success", "data": data}), 200

# 2. API: Mengambil detail 1 pasien spesifik
@app.route('/api/pasien/<int:id>', methods=['GET'])
def get_detail_pasien(id):
    p = RiwayatTriase.query.get(id)
    if not p:
        return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
        
    data = {
        "id": p.id,
        "nama_pasien": p.nama_pasien,
        "file_dicom": p.file_dicom,
        "status_kritis": p.status_kritis,
        "probabilitas_max": p.probabilitas_max,
        "organ": {
            "hati": {"status": p.hati_status, "conf": p.hati_conf},
            "ginjal": {"status": p.ginjal_status, "conf": p.ginjal_conf},
            "limpa": {"status": p.limpa_status, "conf": p.limpa_conf},
            "usus": {"status": p.usus_status, "conf": p.usus_conf}
        }
    }
    return jsonify({"status": "success", "data": data}), 200

# 3. API: Upload gambar dan proses AI
@app.route('/api/upload', methods=['POST'])
def upload_dicom():
    file = request.files.get('file_dicom')
    nama = request.form.get('nama_pasien')

    if not file or file.filename == '':
        return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Lempar gambar ke AI
        hasil = predict_trauma(filepath)
        
        # Simpan ke Database
        pasien_baru = RiwayatTriase(
            nama_pasien=nama, 
            file_dicom=filename,
            status_kritis=hasil['status_kritis'], 
            probabilitas_max=hasil['probabilitas_max'],
            hati_status=hasil['hati']['status'], hati_conf=hasil['hati']['conf'],
            ginjal_status=hasil['ginjal']['status'], ginjal_conf=hasil['ginjal']['conf'],
            limpa_status=hasil['limpa']['status'], limpa_conf=hasil['limpa']['conf'],
            usus_status=hasil['usus']['status'], usus_conf=hasil['usus']['conf']
        )
        db.session.add(pasien_baru)
        db.session.commit()

        # Kembalikan ID pasien yang baru saja dibuat agar React bisa langsung redirect ke halaman detail
        return jsonify({
            "status": "success", 
            "message": "Analisis selesai", 
            "id_pasien": pasien_baru.id
        }), 201

    except Exception as e:
        # TAMBAHKAN DUA BARIS INI BIAR ERRORNYA KELIHATAN DI TERMINAL
        import traceback
        traceback.print_exc()
        
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Jalankan server API di port 5000
    app.run(debug=True, port=5000)