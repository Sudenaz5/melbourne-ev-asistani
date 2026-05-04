import streamlit as st
import uvicorn
import threading
import os
import sys

# 1. Klasör yollarını ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 2. FastAPI (Backend) kısmını içe aktar veya tanımla
# Not: Mevcut FastAPI 'app' nesnenin bu dosyanın içinde olduğunu varsayıyorum.
# Eğer başka dosyadaysa: from backend_dosyan import app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# AI servisini yükle
try:
    from ai import ai_service
except Exception as e:
    print(f"AI Servisi Hatası: {e}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoint'lerin (Önceki kodundan gelenler)
@app.post("/predict")
async def tahmin_yap(veri: dict):
    sonuc = ai_service.tahmin_uret(veri)
    return {"tahmini_fiyat": sonuc}

@app.post("/recommendations")
async def get_recommendations(req: dict):
    return ai_service.get_recommendations(**req)

# Frontend klasörünü bağla
frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# 3. FastAPI'yi arka planda başlatma fonksiyonu
def run_api():
    # Streamlit Cloud üzerinde 8000 portunda çalıştırıyoruz
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Thread başlat (Eğer daha önce başlatılmadıysa)
if "api_started" not in st.session_state:
    threading.Thread(target=run_api, daemon=True).start()
    st.session_state["api_started"] = True

# 4. STREAMLIT ARAYÜZÜ (Bu kısım "Oh no" hatasını siler)
st.set_page_config(page_title="Melbourne Ev Asistanı", page_icon="🏠")

st.success("🚀 Sistem Başarıyla Başlatıldı!")
st.balloons() # İlk açılışta kutlama yapalım

st.markdown("""
### 🏠 Melbourne Ev Karar Asistanı Aktif!
Senin hazırladığın özel frontend arayüzü şu an arka planda servis ediliyor. 

**Not:** Streamlit Cloud genellikle doğrudan 8000 portunu dışarı açmaz. 
Eğer arayüzünü göremiyorsan, yukarıdaki butona tıklayarak manuel tahmin panelini kullanabilirsin.
""")

if st.button("Hızlı Tahmin Panelini Aç"):
    st.info("Bu buton, frontend ile backend arasındaki bağı test etmek içindir.")
