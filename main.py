import streamlit as st
import streamlit.components.v1 as components
import os
import sys

# 1. Klasör yollarını ve AI servisini bağla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

try:
    from ai import ai_service
    model_ok = ai_service.model is not None
except Exception as e:
    st.error(f"Başlatma Hatası: {e}")
    model_ok = False

# 2. Sayfa Yapılandırması
st.set_page_config(page_title="Melbourne Ev Asistanı", layout="wide")

# 3. Kendi Arayüzünü Yükle (Frontend)
frontend_path = os.path.join(BASE_DIR, "frontend", "index.html")

if os.path.exists(frontend_path):
    # HTML dosyasını oku
    with open(frontend_path, "r", encoding="utf-8") as f:
        html_markup = f.read()
    
    # Kendi tasarımını Streamlit ekranına göm
    # height değerini arayüzünün uzunluğuna göre artırabilirsin (örn: 1200)
    components.html(html_markup, height=1000, scrolling=True)
else:
    st.error(f"Hata: {frontend_path} adresinde index.html bulunamadı!")

# 4. Model Durumunu Kontrol Et (Opsiyonel - Sidebar'da gizli durabilir)
if not model_ok:
    st.sidebar.warning("⚠️ Model dosyası yüklenemedi!")
else:
    st.sidebar.success("✅ Model Aktif")
