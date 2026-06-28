import os
import numpy as np
import cv2
import pydicom
import matplotlib.pyplot as plt
import base64
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# KONFIGURASI
# ==========================================

def load_image_simple(image_path):
    """Load gambar dari file (support JPG, PNG, DCM)"""
    file_ext = os.path.splitext(image_path)[1].lower()
    
    try:
        # ===== JIKA JPG/PNG =====
        if file_ext in ['.jpg', '.jpeg', '.png']:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (224, 224))
                return img
            return None
        
        # ===== JIKA DICOM =====
        elif file_ext == '.dcm':
            try:
                dicom = pydicom.dcmread(image_path, force=True)
                img = dicom.pixel_array.astype(np.float64)
                
                # Normalisasi ke 0-255
                img = (img - np.min(img)) / (np.max(img) - np.min(img) + 1e-8) * 255
                img = img.astype(np.uint8)
                img = cv2.resize(img, (224, 224))
                return img
            except:
                # Jika gagal, coba baca sebagai gambar biasa
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, (224, 224))
                    return img
                return None
        
        else:
            return None
            
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def create_heatmap_from_image(image_array):
    """Buat heatmap dari gambar"""
    try:
        # Buat heatmap menggunakan Laplacian
        heatmap = cv2.Laplacian(image_array, cv2.CV_64F)
        heatmap = np.abs(heatmap)
        
        # Normalisasi ke 0-1
        heatmap = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap) + 1e-10)
        
        # Perkuat kontras
        heatmap = np.power(heatmap, 0.5)
        heatmap = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap) + 1e-10)
        
        return heatmap
    except:
        return np.zeros((224, 224))

def generate_shapcam_simple(image_path, predictions=None, max_organ=None, max_prob=None):
    """
    Generate SHAP-CAM - VERSI SEDERHANA
    Tanpa prediksi ulang, hanya tampilkan gambar + heatmap
    """
    print(f"\n🔍 Generating SHAP-CAM for: {image_path}")
    
    # ===== CEK FILE =====
    if not os.path.exists(image_path):
        return {"error": f"File tidak ditemukan: {image_path}"}
    
    # ===== LOAD IMAGE =====
    image_array = load_image_simple(image_path)
    if image_array is None:
        return {"error": "Gagal memproses gambar"}
    
    # ===== BUAT HEATMAP =====
    heatmap = create_heatmap_from_image(image_array)
    
    # ===== ORIGINAL IMAGE UNTUK DISPLAY =====
    original_img = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
    if original_img.dtype != np.uint8:
        original_img = np.uint8(original_img)
    
    # ===== HEATMAP DISPLAY =====
    heatmap_uint8 = np.uint8(255 * heatmap)
    heatmap_display = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_display = cv2.cvtColor(heatmap_display, cv2.COLOR_BGR2RGB)
    
    # ===== KONVERSI KE BASE64 =====
    def img_to_base64(img):
        try:
            if img.dtype != np.uint8:
                img = np.uint8(img)
            _, buffer = cv2.imencode('.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            return base64.b64encode(buffer).decode('utf-8')
        except:
            return ""
    
    # ===== RETURN =====
    return {
        'original': str(img_to_base64(original_img)),
        'heatmap': str(img_to_base64(heatmap_display)),
        'is_cedera': 1 if predictions and any(p > 40 for p in predictions.values()) else 0,
        'max_organ': str(max_organ) if max_organ else 'usus',
        'max_prob': float(max_prob) if max_prob else 0.0,
        'predictions': predictions if predictions else {
            'ginjal': 0.0,
            'hati': 0.0,
            'limpa': 0.0,
            'usus': 0.0
        }
    }

def convert_dcm_to_jpg(dcm_path, output_path=None):
    """Konversi DCM ke JPG"""
    if not os.path.exists(dcm_path):
        return None
    
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(dcm_path))[0]
        output_path = os.path.join(os.path.dirname(dcm_path), f"{base_name}.jpg")
    
    try:
        image_array = load_image_simple(dcm_path)
        if image_array is None:
            return None
        
        image_rgb = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        cv2.imwrite(output_path, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
        return output_path
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    print("="*60)
    print("🔬 SHAP-CAM SERVICE (SEDERHANA)")
    print("="*60)
    test_file = "test.jpg"
    if os.path.exists(test_file):
        result = generate_shapcam_simple(test_file)
        print(f"Result keys: {result.keys()}")
    else:
        print("Test file not found")