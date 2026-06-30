import os
import numpy as np
import pydicom
import zipfile
import cv2
from PIL import Image
import tensorflow as tf
# Ganti dengan ini:
from keras.applications.mobilenet_v2 import preprocess_input

# ==========================================================
# MANTRA SAKTI: Paksa pakai Keras 2 agar format .h5 terbaca
# ==========================================================
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import numpy as np
import pydicom
import cv2
from PIL import Image
import tensorflow as tf
# (dan import-import lainnya)

# ==========================================
# 1. LOAD MODEL KERAS (VERSI .h5)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Arahkan kembali ke .h5
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best_mobilenetv2_model.h5')

# Trik Windows
MODEL_PATH = MODEL_PATH.replace('\\', '/')

try:
    print(f"Mencoba memuat model dari: {MODEL_PATH}")
    # Load model tanpa compile
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ MANTAP! Model MobileNetV2 format .h5 berhasil diload!")
except Exception as e:
    model = None
    print(f"❌ WARNING: Model gagal diload! Error: {e}")

# ==========================================
# 2. PREPROCESSING CITRA UNTUK MOBILENETV2
# ==========================================
def proses_citra_ke_mobilenet(file_path):
    """
    Proses file DICOM/JPG/PNG ke format (224, 224, 3) 
    sesuai syarat input MobileNetV2
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.dcm':
        try:
            dicom = pydicom.dcmread(file_path)
            img = dicom.pixel_array.astype(np.float64)
            # Normalisasi 0-255
            img = ((img - np.min(img)) / (np.max(img) - np.min(img) + 1e-8) * 255).astype(np.uint8)
            # MobileNet butuh 3 channel (RGB), jadi kita duplikasi channel grayscale-nya
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        except Exception as e:
            print(f"Error reading DICOM: {e}, fallback ke PIL/CV2")
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img = cv2.imread(file_path)
        if img is None:
            # Fallback pakai PIL jika CV2 gagal
            img = Image.open(file_path).convert('RGB')
            img = np.array(img)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. Resize ke 224x224
    img = cv2.resize(img, (224, 224))
    # 2. Expand dimensi menjadi (1, 224, 224, 3) untuk batch
    img_array = np.expand_dims(img, axis=0)
    # 3. Preprocessing bawaan MobileNetV2 (skala piksel -1 hingga 1)
    img_array = preprocess_input(img_array.astype(np.float32))
    
    return img_array

# ==========================================
# 3. FUNGSI PREDIKSI UTAMA
# ==========================================
def predict_trauma(image_path):
    """Prediksi trauma menggunakan MobileNetV2"""
    img_array = proses_citra_ke_mobilenet(image_path)
    
    if model:
        # Lakukan inferensi
        preds = model.predict(img_array)
        
        # Karena modelmu menggunakan multi-output (4 organ),
        # urutannya sesuai saat training: ['Ginjal', 'Hati', 'Limpa', 'Usus']
        if isinstance(preds, list):
            prob_ginjal = float(preds[0][0][0]) * 100
            prob_hati = float(preds[1][0][0]) * 100
            prob_limpa = float(preds[2][0][0]) * 100
            prob_usus = float(preds[3][0][0]) * 100
        else:
            # Jika ter-compile sebagai 1 array matriks
            prob_ginjal = float(preds[0][0]) * 100
            prob_hati = float(preds[0][1]) * 100
            prob_limpa = float(preds[0][2]) * 100
            prob_usus = float(preds[0][3]) * 100
    else:
        prob_ginjal, prob_hati, prob_limpa, prob_usus = 0.0, 0.0, 0.0, 0.0

    # Gunakan threshold 50.0% karena aktivasi terakhirmu adalah sigmoid (0.5)
    threshold = 50.0 
    
    status_hati = "Cedera" if prob_hati > threshold else "Sehat"
    status_ginjal = "Cedera" if prob_ginjal > threshold else "Sehat"
    status_limpa = "Cedera" if prob_limpa > threshold else "Sehat"
    status_usus = "Cedera" if prob_usus > threshold else "Sehat"

    is_kritis = 1 if any(p > threshold for p in [prob_hati, prob_ginjal, prob_limpa, prob_usus]) else 0
    max_prob = max([prob_hati, prob_ginjal, prob_limpa, prob_usus])

    # Format return disamakan persis agar app.py tidak error
    return {
        "status_kritis": is_kritis,
        "probabilitas_max": round(max_prob, 2),
        "hati": {"status": status_hati, "conf": round(prob_hati, 2)},
        "ginjal": {"status": status_ginjal, "conf": round(prob_ginjal, 2)},
        "limpa": {"status": status_limpa, "conf": round(prob_limpa, 2)},
        "usus": {"status": status_usus, "conf": round(prob_usus, 2)}
    }