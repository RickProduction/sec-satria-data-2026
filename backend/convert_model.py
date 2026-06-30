import tensorflow as tf
import os

# Load model dari file yang tadi kamu download
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'MobileNetV2_MultiLabel_20260629_1413.keras')
model = tf.keras.models.load_model(MODEL_PATH)

# Simpan ke format .h5
model.save('best_mobilenetv2_model.h5')
print("✅ Konversi ke .h5 berhasil!")