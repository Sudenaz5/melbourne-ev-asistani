import streamlit as st
import uvicorn
import threading
import os
import sys

# Klasör yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# FastAPI uygulamasını oluştur
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# AI servisini en başta, Streamlit context'ine girmeden yükle
try:
    from ai import ai_service
except Exception as e:
    print(f"Başlangıç hatası: {e}")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/predict")
async def tahmin(veri: dict):
    return {"tahmini_fiyat": ai_service.tahmin_uret(veri)}

# Arayüz dosyalarını bağla
frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/site", StaticFiles(directory=frontend_path, html=True), name="frontend")

# API'yi Streamlit'ten bağımsız bir thread'de başlat
if not hasattr(st, 'api_started'):
    def run():
        uvicorn.run(app, host="0.0.0.0", port=8000)
    threading.Thread(target=run, daemon=True).start()
    st.api_started = True

# STREAMLIT ARAYÜZÜ
st.set_page_config(page_title="Melbourne Ev Asistanı")
st.title("🏠 Melbourne Ev Karar Asistanı")
st.success("✅ Backend sunucusu port 8000 üzerinde aktif!")

st.markdown(f"""
### 🚀 Uygulama Yayında!
Modeliniz başarıyla yüklendi. Hazırladığınız özel arayüze erişmek için:
1. Streamlit URL'nizin sonuna `/site/` ekleyerek deneyin.
2. Ya da aşağıdaki butona basarak tahmin üretin.
""")

if st.button("Tahmin Test Et"):
    st.write("Model Durumu:", "Yüklendi" if ai_service.model else "Hata!")
