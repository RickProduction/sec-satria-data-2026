import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from ml_pipeline import predict_trauma
from shapcam_service import generate_shapcam_simple, convert_dcm_to_jpg

app = Flask(__name__)

# Wajib untuk mengizinkan React mengakses Flask
CORS(app)

# Konfigurasi Database (Ganti sesuai setting MySQL kamu)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/db_abdominaltrauma'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Lokasi penyimpanan gambar
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# ===== VALIDASI EKSTENSI FILE =====
ALLOWED_EXTENSIONS = {'dcm', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Cek apakah ekstensi file diperbolehkan"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# ===== MODEL DATABASE =====
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
# ENDPOINT API
# ==========================================

# 1. API: Mengambil semua data antrean pasien
@app.route('/api/pasien', methods=['GET'])
def get_semua_pasien():
    """Mengambil semua data pasien yang sudah terdaftar"""
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
    """Mengambil detail lengkap 1 pasien berdasarkan ID"""
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
    """Upload gambar (support .dcm, .jpg, .jpeg, .png) dan proses prediksi"""
    file = request.files.get('file_dicom')
    nama = request.form.get('nama_pasien')

    if not file or file.filename == '':
        return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "status": "error", 
            "message": "Format file tidak didukung. Gunakan .dcm, .jpg, .jpeg, atau .png"
        }), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        hasil = predict_trauma(filepath)
        
        pasien_baru = RiwayatTriase(
            nama_pasien=nama, 
            file_dicom=filename,
            status_kritis=hasil['status_kritis'], 
            probabilitas_max=hasil['probabilitas_max'],
            hati_status=hasil['hati']['status'], 
            hati_conf=hasil['hati']['conf'],
            ginjal_status=hasil['ginjal']['status'], 
            ginjal_conf=hasil['ginjal']['conf'],
            limpa_status=hasil['limpa']['status'], 
            limpa_conf=hasil['limpa']['conf'],
            usus_status=hasil['usus']['status'], 
            usus_conf=hasil['usus']['conf']
        )
        db.session.add(pasien_baru)
        db.session.commit()

        return jsonify({
            "status": "success", 
            "message": "Analisis selesai", 
            "id_pasien": pasien_baru.id
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. API: SHAP-CAM untuk pasien berdasarkan ID (PAKAI DATA DARI DATABASE)
@app.route('/api/shapcam/pasien/<int:id>', methods=['GET'])
def api_shapcam_pasien(id):
    """Generate SHAP-CAM untuk pasien berdasarkan ID - PAKAI DATA DARI DATABASE"""
    p = RiwayatTriase.query.get(id)
    if not p:
        return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
    
    # Cari file di berbagai kemungkinan lokasi
    possible_paths = [
        os.path.join(app.config['UPLOAD_FOLDER'], p.file_dicom),
        os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(p.file_dicom)[0] + '.jpg'),
        os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(p.file_dicom)[0] + '.png'),
    ]
    
    filepath = None
    for path in possible_paths:
        if os.path.exists(path):
            filepath = path
            break
    
    if filepath is None:
        return jsonify({
            "status": "error", 
            "message": f"File gambar tidak ditemukan"
        }), 404
    
    print(f"📂 Processing SHAP-CAM for: {filepath}")
    
    try:
        # ===== AMBIL DATA PREDIKSI DARI DATABASE =====
        predictions = {
            'ginjal': float(p.ginjal_conf or 0),
            'hati': float(p.hati_conf or 0),
            'limpa': float(p.limpa_conf or 0),
            'usus': float(p.usus_conf or 0)
        }
        
        # Cari organ dengan probabilitas tertinggi
        max_organ = max(predictions, key=predictions.get)
        max_prob = float(predictions[max_organ])
        
        print(f"📊 Data dari database:")
        print(f"   Predictions: {predictions}")
        print(f"   Max Organ: {max_organ} ({max_prob}%)")
        
        # ===== GENERATE SHAP-CAM =====
        result = generate_shapcam_simple(
            filepath, 
            predictions=predictions,
            max_organ=max_organ,
            max_prob=max_prob
        )
        
        if 'error' in result:
            return jsonify({"status": "error", "message": result['error']}), 500
        
        return jsonify({
            "status": "success",
            "data": {
                "id_pasien": int(p.id),
                "nama_pasien": str(p.nama_pasien),
                "is_cedera": int(result.get('is_cedera', 0)),
                "max_organ": str(result.get('max_organ', '')),
                "max_prob": float(result.get('max_prob', 0)),
                "predictions": {
                    "ginjal": float(predictions.get('ginjal', 0)),
                    "hati": float(predictions.get('hati', 0)),
                    "limpa": float(predictions.get('limpa', 0)),
                    "usus": float(predictions.get('usus', 0))
                },
                "original": str(result.get('original', '')),
                "heatmap": str(result.get('heatmap', ''))
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 5. API: Konversi DCM ke JPG
@app.route('/api/convert-dcm', methods=['POST'])
def api_convert_dcm():
    """Konversi file DICOM (.dcm) ke JPG"""
    file = request.files.get('file')
    
    if not file or file.filename == '':
        return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400
    
    if not file.filename.lower().endswith('.dcm'):
        return jsonify({"status": "error", "message": "File harus berekstensi .dcm"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        jpg_path = convert_dcm_to_jpg(filepath)
        
        if jpg_path is None:
            return jsonify({"status": "error", "message": "Gagal konversi DCM"}), 500
        
        import base64
        with open(jpg_path, 'rb') as f:
            jpg_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            "status": "success",
            "data": {
                "jpg_filename": os.path.basename(jpg_path),
                "jpg_base64": jpg_base64
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 6. API: Hapus data pasien
@app.route('/api/pasien/<int:id>', methods=['DELETE'])
def hapus_pasien(id):
    """Menghapus data pasien berdasarkan ID"""
    p = RiwayatTriase.query.get(id)
    if not p:
        return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], p.file_dicom)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
    
    db.session.delete(p)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Data berhasil dihapus"}), 200

# ==========================================
# ERROR HANDLER
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Endpoint tidak ditemukan"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Terjadi kesalahan server"}), 500

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    print("="*60)
    print("🚀 SERVER ABDOMINAL TRAUMA DETECTION")
    print("="*60)
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Allowed extensions: .dcm, .jpg, .jpeg, .png")
    print("="*60)
    print("🌐 Server running on: http://localhost:5000")
    print("📋 API Endpoints:")
    print("   GET  /api/pasien              - Semua pasien")
    print("   GET  /api/pasien/<id>         - Detail pasien")
    print("   POST /api/upload              - Upload + Prediksi")
    print("   GET  /api/shapcam/pasien/<id> - SHAP-CAM pasien")
    print("   POST /api/convert-dcm         - Konversi DCM ke JPG")
    print("   DELETE /api/pasien/<id>       - Hapus pasien")
    print("="*60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')