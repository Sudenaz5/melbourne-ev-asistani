import streamlit as st
import uvicorn
import threading
import os
import sys

# Klasör yollarını sisteme tanıt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# FastAPI ve Middleware kurulumu
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# AI servisini thread dışında, en başta yükle
try:
    from ai import ai_service
except Exception as e:
    print(f"AI Import Hatası: {e}")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/predict")
async def predict_api(veri: dict):
    return {"tahmini_fiyat": ai_service.tahmin_uret(veri)}

# Frontend klasörünü /site yoluna bağla
frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/site", StaticFiles(directory=frontend_path, html=True), name="frontend")

# FastAPI sunucusunu başlat
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if "api_started" not in st.session_state:
    threading.Thread(target=run_fastapi, daemon=True).start()
    st.session_state["api_started"] = True

# --- STREAMLIT GÖRSEL EKRANI ---
st.set_page_config(page_title="Melbourne Emlak Sistemi", layout="wide")
st.title("🏠 Melbourne Ev Karar Asistanı")

if ai_service.model:
    st.success("✅ Model ve Backend Başarıyla Yüklendi!")
    st.balloons()
else:
    st.error("⚠️ Model henüz yüklenemedi. Logları kontrol edin.")

st.info("Kendi arayüzünüze erişmek için URL sonuna '/site/' ekleyin.")
