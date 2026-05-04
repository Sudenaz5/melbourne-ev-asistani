import streamlit as st
import streamlit.components.v1 as components
import os
import sys

# Klasör yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# AI Servisini Yükle
try:
    from ai import ai_service
    model_ok = ai_service.model is not None
except Exception as e:
    st.error(f"AI Yükleme Hatası: {e}")
    model_ok = False

st.set_page_config(page_title="Melbourne Ev Asistanı", layout="wide")

# Klasör kontrolü için log basalım
frontend_dir = os.path.join(BASE_DIR, "frontend")
html_path = os.path.join(frontend_dir, "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # CSS ve JS dosyalarının yollarını Streamlit'in anlayacağı hale getirmek zor olabilir.
    # Bu yüzden sadece HTML'i değil, her şeyi kapsayan bir yükleme yapalım.
    st.markdown("### 🏠 Melbourne Ev Karar Asistanı")
    components.html(html_content, height=1200, scrolling=True)
else:
    st.error(f"Hata: index.html bulunamadı! Aranan yol: {html_path}")
    st.write("Mevcut klasör içeriği:", os.listdir(BASE_DIR))
    if os.path.exists(frontend_dir):
        st.write("Frontend klasörü içeriği:", os.listdir(frontend_dir))

# Sidebar durumu
if model_ok:
    st.sidebar.success("✅ Model Aktif")
else:
    st.sidebar.warning("⚠️ Model Yüklenemedi")
