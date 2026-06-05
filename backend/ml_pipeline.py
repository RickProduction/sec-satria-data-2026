import joblib
import numpy as np
import os

# Load model Random Forest yang sudah dilatih
# Pastikan file random_forest.pkl sudah ada di folder models/
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'random_forest.pkl')

try:
    rf_model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    rf_model = None
    print("Warning: Model random_forest.pkl belum ada. Gunakan mode simulasi.")

def extract_features(image_path):
    """
    Fungsi ini untuk mengekstrak fitur statistik/tekstur dari gambar CT Scan.
    SESUAIKAN DENGAN KODE EKSTRAKSI FITUR ASLI KALIAN.
    """
    # Contoh output dummy array 1D (misal ada 10 fitur)
    dummy_features = np.random.rand(1, 10) 
    return dummy_features

def predict_trauma(image_path):
    """
    Menjalankan prediksi dan mengembalikan status tiap organ beserta confidence-nya.
    """
    features = extract_features(image_path)
    
    if rf_model:
        # Jika model asli ada, gunakan predict_proba
        # Sesuaikan urutan output sesuai training kalian
        probabilities = rf_model.predict_proba(features)
        
        # Asumsi output probabilitas untuk simplifikasi contoh
        any_injury_prob = probabilities[0][1] * 100 
    else:
        # SIMULASI jika file .pkl belum siap
        any_injury_prob = np.random.randint(20, 99)

    # Menentukan status berdasarkan threshold (Minimalisasi False Negative)
    # Jika probabilitas cedera > 30%, kita set sebagai indikasi cedera
    is_injured = 1 if any_injury_prob > 30 else 0

    # Output dictionary yang akan dikirim ke Backend/Frontend
    return {
        "any_injury": is_injured,
        "confidence": round(any_injury_prob, 2),
        "liver_status": "high_injury" if any_injury_prob > 70 else "healthy",
        "kidney_status": "low_injury" if 30 < any_injury_prob <= 70 else "healthy",
        "spleen_status": "healthy",
        "bowel_status": "healthy"
    }