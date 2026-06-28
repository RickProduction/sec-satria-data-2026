import os
import joblib
import numpy as np
import pydicom
import cv2
from scipy.stats import skew, kurtosis
from PIL import Image

# Load Model saat aplikasi dijalankan
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'rf_multiorgan_trauma.pkl')
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"WARNING: Model gagal diload! Error: {e}")

def proses_dicom_ke_hu(file_path):
    """Proses file DICOM ke HU (Hounsfield Unit)"""
    dicom = pydicom.dcmread(file_path)
    image = dicom.pixel_array.astype(np.float64)

    intercept = dicom.RescaleIntercept if 'RescaleIntercept' in dicom else 0.0
    slope = dicom.RescaleSlope if 'RescaleSlope' in dicom else 1.0
    hu_image = image * slope + intercept

    hu_image = np.clip(hu_image, -50, 150)
    hu_image = ((hu_image - (-50)) / 200 * 255).astype(np.uint8)
    hu_image = cv2.resize(hu_image, (128, 128))
    return hu_image

def proses_jpg_ke_hu(file_path):
    """Proses file JPG/PNG ke format yang sama dengan DICOM"""
    # Baca gambar
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        # Coba dengan PIL
        img = Image.open(file_path).convert('L')
        img = np.array(img)
    
    # Resize ke 128x128
    img = cv2.resize(img, (128, 128))
    
    # Normalisasi ke 0-255
    img = ((img - np.min(img)) / (np.max(img) - np.min(img) + 1e-8) * 255).astype(np.uint8)
    
    return img

def ekstraksi_fitur_statistik(image):
    return [
        np.mean(image),          
        np.std(image),           
        np.var(image),           
        skew(image.flatten()),   
        kurtosis(image.flatten())
    ]

def predict_trauma(image_path):
    """Prediksi trauma dari file (support .dcm, .jpg, .jpeg, .png)"""
    file_ext = os.path.splitext(image_path)[1].lower()
    
    # Pilih proses berdasarkan ekstensi file
    if file_ext == '.dcm':
        try:
            gambar_hu = proses_dicom_ke_hu(image_path)
        except Exception as e:
            print(f"Error reading DICOM: {e}")
            # Jika gagal, coba baca sebagai gambar biasa
            gambar_hu = proses_jpg_ke_hu(image_path)
    else:
        gambar_hu = proses_jpg_ke_hu(image_path)
    
    features = np.array([ekstraksi_fitur_statistik(gambar_hu)])
    
    if model:
        probs = model.predict_proba(features)
        
        def aman_ambil_prob_cedera(prob_array):
            if len(prob_array[0]) > 1:
                return prob_array[0][1] * 100
            else:
                return 0.0

        prob_hati = aman_ambil_prob_cedera(probs[0])
        prob_ginjal = aman_ambil_prob_cedera(probs[1])
        prob_limpa = aman_ambil_prob_cedera(probs[2])
        prob_usus = aman_ambil_prob_cedera(probs[3])
    else:
        prob_hati, prob_ginjal, prob_limpa, prob_usus = 0.0, 0.0, 0.0, 0.0

    threshold = 40.0
    
    status_hati = "Cedera" if prob_hati > threshold else "Sehat"
    status_ginjal = "Cedera" if prob_ginjal > threshold else "Sehat"
    status_limpa = "Cedera" if prob_limpa > threshold else "Sehat"
    status_usus = "Cedera" if prob_usus > threshold else "Sehat"

    is_kritis = 1 if any(p > threshold for p in [prob_hati, prob_ginjal, prob_limpa, prob_usus]) else 0
    max_prob = max([prob_hati, prob_ginjal, prob_limpa, prob_usus])

    return {
        "status_kritis": is_kritis,
        "probabilitas_max": round(max_prob, 2),
        "hati": {"status": status_hati, "conf": round(prob_hati, 2)},
        "ginjal": {"status": status_ginjal, "conf": round(prob_ginjal, 2)},
        "limpa": {"status": status_limpa, "conf": round(prob_limpa, 2)},
        "usus": {"status": status_usus, "conf": round(prob_usus, 2)}
    }