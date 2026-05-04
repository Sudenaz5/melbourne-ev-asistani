import streamlit as st
import os
import sys

# Klasör yollarını ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# AI Servisini Yükle (Doğrudan import)
try:
    from ai import ai_service
    model_ok = ai_service.model is not None
except Exception as e:
    st.error(f"Başlatma Hatası: {e}")
    model_ok = False

st.set_page_config(page_title="Melbourne Ev Asistanı", layout="wide")

if model_ok:
    st.success("🏠 Melbourne Ev Karar Asistanı Hazır!")
    st.balloons()
    
    # Senin ai_service içindeki fonksiyonu doğrudan burada kullanıyoruz
    st.sidebar.header("Tahmin Paneli")
    oda = st.sidebar.slider("Oda Sayısı", 1, 8, 3)
    yas = st.sidebar.number_input("Bina Yaşı", 0, 100, 10)
    
    if st.sidebar.button("Fiyatı Tahmin Et"):
        sonuc = ai_service.tahmin_uret({'oda_sayisi': oda, 'bina_yasi': yas})
        st.metric("Tahmini Ev Değeri", f"{sonuc:,.0f} AUD")
else:
    st.error("Model dosyası yüklenemedi. Lütfen logları kontrol edin.")
