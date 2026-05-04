import streamlit as st
import os
import sys

# Klasör yollarını ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# AI Servisini Yükle
try:
    from ai import ai_service
    # Model yüklenmiş mi kontrol et (ai_service içinde joblib.load var)
    model_durumu = "Yüklendi ✅" if ai_service.model is not None else "Yüklenemedi ❌"
except Exception as e:
    model_durumu = f"Hata: {e}"

# STREAMLIT ARAYÜZÜ
st.set_page_config(page_title="Melbourne Ev Asistanı", layout="wide")

st.title("🏠 Melbourne Ev Karar Asistanı")
st.write(f"**Model Durumu:** {model_durumu}")

if ai_service.model is None:
    st.error("Model dosyası (.pkl) bulunamadı. Lütfen 'final_model.zip' dosyasının doğru yerde olduğunu kontrol edin.")
    st.info(f"Aranan yerler: {BASE_DIR} veya {os.path.join(BASE_DIR, 'ai')}")
else:
    st.success("Sistem hazır! Tahmin yapmaya başlayabilirsiniz.")
    st.balloons()

# Yan panelde basit bir test arayüzü
with st.sidebar:
    st.header("Hızlı Tahmin")
    oda = st.slider("Oda Sayısı", 1, 5, 3)
    bina_yasi = st.number_input("Bina Yaşı", 0, 100, 10)
    
    if st.button("Fiyat Tahmin Et"):
        # Doğrudan ai_service fonksiyonunu kullanıyoruz, API'ye gerek yok!
        test_veri = {'oda_sayisi': oda, 'bina_yasi': bina_yasi}
        sonuc = ai_service.tahmin_uret(test_veri)
        st.metric("Tahmini Fiyat", f"{sonuc:,.0f} AUD")
