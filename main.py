import streamlit as st
import uvicorn
import threading
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. Klasör ve Yol Ayarları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# AI Servisini Yükle
try:
    from ai import ai_service
except Exception as e:
    st.error(f"AI Servisi yüklenirken hata oluştu: {e}")

# 2. FastAPI (Backend) Tanımlama
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def tahmin_yap(veri: dict):
    sonuc = ai_service.tahmin_uret(veri)
    fiyat = sonuc if isinstance(sonuc, (int, float)) else 0
    return {"tahmini_fiyat": fiyat}

@app.post("/recommendations")
async def get_recommendations(req: dict):
    # Gelen veriyi ai_service'e aktar
    recs = ai_service.get_recommendations(**req)
    return recs

# Frontend dosyalarını bağla
frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# 3. FastAPI'yi Arka Planda Başlatma (Thread)
def run_api():
    # Streamlit Cloud üzerinde 8000 portunda çalıştırıyoruz
    uvicorn.run(app, host="127.0.0.1", port=8000)

if "api_started" not in st.session_state:
    thread = threading.Thread(target=run_api, daemon=True)
    thread.start()
    st.session_state["api_started"] = True

# 4. Streamlit Görsel Arayüzü (Oh No Hatasını Giderir)
st.set_page_config(page_title="Melbourne Emlak Asistanı", layout="wide")

st.success("✅ Backend Sunucusu Başarıyla Başlatıldı!")
st.balloons()

st.title("🏠 Melbourne Ev Karar Asistanı")
st.markdown("""
### Sistem Aktif!
Senin hazırladığın özel HTML/JS arayüzü şu an arka planda servis ediliyor. 
Streamlit Cloud kısıtlamaları nedeniyle doğrudan 8000 portuna erişemiyor olabilirsin.
""")

st.info("Eğer kendi arayüzün açılmazsa, tahminleri buradan manuel olarak da yapabilirsin.")
