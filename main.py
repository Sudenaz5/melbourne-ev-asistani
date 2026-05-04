from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from ai import ai_service

app = FastAPI(title="Emlak Projesi API")

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

class RecommendationRequest(BaseModel):
    profil_id: str
    min_price: float
    max_price: float
    max_distance_str: str
    oncelik_id: str
    ev_tipi_id: str
    min_banyo: int
    min_garaj: int

@app.post("/recommendations")
async def get_recommendations(req: RecommendationRequest):
    recs = ai_service.get_recommendations(
        req.profil_id, req.min_price, req.max_price, req.max_distance_str,
        req.oncelik_id, req.ev_tipi_id, req.min_banyo, req.min_garaj
    )
    return recs

@app.get("/market-data")
async def get_market_data():
    return ai_service.get_market_data()

frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")