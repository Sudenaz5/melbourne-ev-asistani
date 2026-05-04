import pandas as pd
import numpy as np
import joblib
import os
import zipfile

# Mevcut dosyanın konumunu al (ai klasörü)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "melb_data.csv")

# Model yollarını ayarla
ZIP_PATH = os.path.join(BASE_DIR, 'final_model.zip') # Zip ai/ klasöründe
MODEL_PATH = os.path.join(BASE_DIR, 'final_model.pkl') # Pkl buraya çıkarılacak

# Model dosyası yoksa zip'ten çıkar
if not os.path.exists(MODEL_PATH):
    if os.path.exists(ZIP_PATH):
        try:
            with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(BASE_DIR)
            print("Model başarıyla zip'ten çıkarıldı.")
        except Exception as e:
            print(f"Zip çıkarma hatası: {e}")
    else:
        print("Hata: final_model.zip bulunamadı!")

# Modeli yükle[cite: 1]
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Model yükleme hatası: {e}")
    model = None

try:
    data = pd.read_csv(DATA_PATH)
    data = data[data["Price"] < 5_000_000]
    for col in ["BuildingArea", "YearBuilt", "Car"]:
        data[col] = data[col].fillna(data[col].median())
    data["Type"] = data["Type"].map({"h": 0, "t": 1, "u": 2})
    data["Regionname"] = data["Regionname"].astype("category").cat.codes
except Exception as e:
    data = pd.DataFrame()

MODEL_FEATURES = ["Rooms", "Distance", "Bathroom", "Car", "BuildingArea", "YearBuilt", "Type", "Regionname"]

PROFILLER = {
    "Yalnız Yaşayan":      {"aciklama": "Çalışan veya öğrenci, pratik ve merkeze yakın",  "min_oda": 1, "ideal_oda": 2},
    "Çift / 2 Kişi":       {"aciklama": "Birlikte yaşayan çift, konfor ve konum önemli",   "min_oda": 2, "ideal_oda": 3},
    "Aile (Çocuklu)":      {"aciklama": "Okul yakınlığı ve geniş alan öncelikli",         "min_oda": 3, "ideal_oda": 4},
    "Arkadaş Grubu":       {"aciklama": "Paylaşımlı yaşam, geniş ortak alanlar",           "min_oda": 3, "ideal_oda": 4},
}

ONCELIK = {
    "Fiyat":    {"fiyat": 0.6, "konum": 0.2, "buyukluk": 0.2},
    "Konum":    {"fiyat": 0.2, "konum": 0.6, "buyukluk": 0.2},
    "Büyüklük": {"fiyat": 0.2, "konum": 0.2, "buyukluk": 0.6},
}

BOLGE_MAP = {
    0:"Eastern Metropolitan", 1:"Eastern Victoria", 2:"Northern Metropolitan",
    3:"Northern Victoria",    4:"South-Eastern Metropolitan",
    5:"Southern Metropolitan", 6:"Western Metropolitan", 7:"Western Victoria"
}

UZAKLIK_MAP = {
    "Çok Yakın (0-5 km)": (0, 5),  "Yakın (5-15 km)": (0, 15),
    "Orta (15-25 km)":   (10, 25), "Uzak (25+ km)":   (20, 60), "Fark Etmez": (0, 60),
}

EV_TIPI_MAP = {"Fark Etmez": None, "Müstakil (h)": 0, "Sıra Ev (t)": 1, "Daire (u)": 2}

def tahmin_uret(veri_dict):
    if model is None:
        return 0

    try:
        yas = int(veri_dict.get('bina_yasi', 10))
        yapim_yili = 2026 - yas

        input_data = {
            "Rooms": int(veri_dict.get('oda_sayisi', 3)),
            "Distance": float(veri_dict.get('bolge_id', 5)),
            "Bathroom": int(veri_dict.get('banyo_sayisi', 1)), 
            "Car": int(veri_dict.get('garaj_sayisi', 1)),     
            "BuildingArea": float(veri_dict.get('metrekare', 120)),
            "YearBuilt": float(yapim_yili), 
            "Type": int(veri_dict.get('ev_tipi', 0)),    
            "Regionname": int(veri_dict.get('bolge_kodu', 2)) 
        }

        df = pd.DataFrame([input_data])[MODEL_FEATURES]
        tahmin = model.predict(df)[0]
        return float(tahmin)
    except Exception as e:
        return str(e)

def get_recommendations(profil_id, min_price, max_price, max_distance_str, oncelik_id, ev_tipi_id, min_banyo, min_garaj):
    if data.empty:
        return {"error": "Veri seti bulunamadı."}
    
    profil = PROFILLER.get(profil_id, PROFILLER["Yalnız Yaşayan"])
    uzak_min, uzak_max = UZAKLIK_MAP.get(max_distance_str, (0, 15))
    
    filtered = data[
        (data["Price"] >= min_price) & 
        (data["Price"] <= max_price) &
        (data["Distance"] >= uzak_min) & 
        (data["Distance"] <= uzak_max) &
        (data["Rooms"] >= profil["min_oda"]) &
        (data["Bathroom"] >= min_banyo) & 
        (data["Car"] >= min_garaj)
    ].copy()
    
    secilen_tip = EV_TIPI_MAP.get(ev_tipi_id)
    if secilen_tip is not None:
        filtered = filtered[filtered["Type"] == secilen_tip]
        
    if len(filtered) == 0:
        return {"uyari": "Bu kriterlere uyan ev bulunamadı. Bütçeni veya uzaklık tercihini genişlet."}

    agirlik = ONCELIK.get(oncelik_id, ONCELIK["Fiyat"])
    
    if len(filtered) > 1:
        fn = 1 - (filtered["Price"] - filtered["Price"].min()) / (filtered["Price"].max() - filtered["Price"].min() + 1)
        kn = 1 - (filtered["Distance"] - filtered["Distance"].min()) / (filtered["Distance"].max() - filtered["Distance"].min() + 1)
        bn = (filtered["Rooms"] - filtered["Rooms"].min()) / (filtered["Rooms"].max() - filtered["Rooms"].min() + 1)
        filtered["skor"] = agirlik["fiyat"]*fn + agirlik["konum"]*kn + agirlik["buyukluk"]*bn
    else:
        filtered["skor"] = 1.0

    # 1. En iyi 3 ev (Ozet)
    ozet = (
        filtered.groupby("Rooms")
        .agg(ort_fiyat=("Price","median"), ort_uzaklik=("Distance","median"),
             ort_arsa=("Landsize","median"), ort_banyo=("Bathroom","median"),
             ort_garaj=("Car", "median"), ort_yapialani=("BuildingArea", "median"),
             ort_yapiyili=("YearBuilt", "median"), ev_sayisi=("Price","count"), skor=("skor","mean"))
        .sort_values("skor", ascending=False).head(3).reset_index()
    )
    
    top_3 = []
    for _, row in ozet.iterrows():
        # Tahmin için
        inp = {
            "Rooms": row["Rooms"], "Distance": row["ort_uzaklik"],
            "Bathroom": row["ort_banyo"], "Car": row["ort_garaj"],
            "BuildingArea": row["ort_yapialani"], "YearBuilt": row["ort_yapiyili"],
            "Type": secilen_tip if secilen_tip is not None else 0,
            "Regionname": 2
        }
        df_inp = pd.DataFrame([inp])[MODEL_FEATURES]
        tahmin = model.predict(df_inp)[0] if model else 0
        
        fark = ((row["ort_fiyat"] - tahmin) / tahmin) * 100 if tahmin else 0
        neden = []
        if fark < -5:   neden.append(f"🔥 Piyasa değerinin %{abs(fark):.0f} altında")
        if fark > 15:   neden.append("⚠️ Bölge ortalamasına göre pahalı")
        if row["ort_uzaklik"] <= 7: neden.append("🚲 Merkeze çok yakın")
        if row["Rooms"] >= profil["ideal_oda"]: neden.append("⭐ Profil için ideal oda sayısı")
        if row["ort_banyo"] >= 2:   neden.append("🚿 Çift banyo")
        if not neden: neden.append("Kriterlerini dengeli karşılıyor")
        
        top_3.append({
            "rooms": int(row["Rooms"]),
            "price": float(row["ort_fiyat"]),
            "distance": float(row["ort_uzaklik"]),
            "count": int(row["ev_sayisi"]),
            "prediction": float(tahmin),
            "reasons": neden
        })

    # 2. Histogram Data (Fiyat dağılımı 20 bin)
    try:
        hist, bins = np.histogram(filtered["Price"], bins=20)
        hist_data = [{"range": f"{int(bins[i]/1000)}k-{int(bins[i+1]/1000)}k", "count": int(hist[i])} for i in range(len(hist))]
    except:
        hist_data = []

    # 3. Oda sayısına göre medyan fiyat
    oda_fiyat_df = filtered.groupby("Rooms")["Price"].median().reset_index()
    oda_fiyat = [{"rooms": int(r["Rooms"]), "price": float(r["Price"])} for _, r in oda_fiyat_df.iterrows()]

    # 4. Kıyaslama Data
    kdf = filtered[["Rooms","Bathroom","Car","Distance","Price","BuildingArea","YearBuilt","Type"]].copy()
    kdf["Type"] = kdf["Type"].map({0:"Müstakil", 1:"Sıra Ev", 2:"Daire"})
    if "Suburb" in data.columns:
        kdf["Suburb"] = data.loc[kdf.index, "Suburb"]
    else:
        kdf["Suburb"] = "—"
        
    kdf["Etiket"] = kdf["Suburb"] + " · " + kdf["Rooms"].astype(int).astype(str) + " oda · " + kdf["Price"].apply(lambda x: f"{x:,.0f} AUD")
    compare_options = kdf.to_dict(orient="records")

    # 5. Harita verisi (Genişletilmiş ve Akıllı)
    # Performans için 1500 nokta alıyoruz
    map_df = data.dropna(subset=["Lattitude","Longtitude"]).sample(min(1500, len(data)), random_state=42).copy()
    map_df["Durum"] = "Diğer"
    
    # Filtrelenmiş evleri "Bütçeye Uygun" yap
    map_df.loc[map_df.index.isin(filtered.index), "Durum"] = "Bütçeye Uygun"
    
    # Diğer kriterleri (oda, mesafe) sağlayıp sadece bütçeyi aşanları bul
    diger_kriterler = (
        (map_df["Distance"] >= uzak_min) & (map_df["Distance"] <= uzak_max) &
        (map_df["Rooms"] >= profil["min_oda"]) &
        (map_df["Bathroom"] >= min_banyo) & 
        (map_df["Car"] >= min_garaj)
    )
    if secilen_tip is not None:
        diger_kriterler = diger_kriterler & (map_df["Type"] == secilen_tip)
        
    map_df.loc[diger_kriterler & (map_df["Price"] > max_price), "Durum"] = "Bütçe Üstü"
    
    # Tahminleri hesapla (sadece hedeflenen evler için, performans amacıyla)
    hedef_indexler = map_df[map_df["Durum"].isin(["Bütçeye Uygun", "Bütçe Üstü"])].index
    map_df["Tahmin"] = 0.0
    if len(hedef_indexler) > 0 and model is not None:
        X_pred = map_df.loc[hedef_indexler, MODEL_FEATURES]
        map_df.loc[hedef_indexler, "Tahmin"] = model.predict(X_pred)
        
    if "Suburb" not in map_df.columns:
        map_df["Suburb"] = map_df["Regionname"].map(BOLGE_MAP)
        
    def get_tooltip_not(row):
        if row["Durum"] == "Bütçeye Uygun":
            return "✅ Bütçenize Uygun"
        elif row["Durum"] == "Bütçe Üstü":
            fark = ((row["Price"] - max_price) / max_price) * 100
            return f"⚠️ Bütçenizi %{fark:.0f} Aşıyor"
        return "—"
        
    map_df["Not"] = map_df.apply(get_tooltip_not, axis=1)
    
    map_data = map_df[["Lattitude", "Longtitude", "Price", "Rooms", "Durum", "Tahmin", "Suburb", "Not"]].to_dict(orient="records")

    # 6. Mahalle Skor Tablosu (Top Neighborhoods)
    if "Suburb" in data.columns:
        mahalle_col = "Suburb"
    else:
        mahalle_col = "Regionname"
        
    mahalle_skor = (
        filtered.groupby(mahalle_col)
        .agg(ort_fiyat=("Price", "median"), ort_skor=("skor", "mean"), ev_sayisi=("Price", "count"))
        .reset_index()
    )
    mahalle_skor = mahalle_skor[mahalle_skor["ev_sayisi"] >= 1] # En az 1 ev
    mahalle_skor["fiyat_performans"] = (mahalle_skor["ort_skor"] / mahalle_skor["ort_fiyat"]) * 1000000
    mahalle_skor = mahalle_skor.sort_values("fiyat_performans", ascending=False).head(3)
    
    top_mahalleler = []
    for _, row in mahalle_skor.iterrows():
        mahalle_ismi = row[mahalle_col]
        if mahalle_col == "Regionname":
            mahalle_ismi = BOLGE_MAP.get(mahalle_ismi, str(mahalle_ismi))
        top_mahalleler.append({
            "isim": mahalle_ismi,
            "ort_fiyat": float(row["ort_fiyat"]),
            "kalite_skoru": float(row["ort_skor"] * 10), # 10 üzerinden
        })

    # 7. Benzer Evler (Carousel için)
    benzer_evler = []
    if len(top_3) > 0:
        top_rooms = top_3[0]["rooms"]
        benzerler_df = filtered[filtered["Rooms"] == top_rooms].sort_values("skor", ascending=False).head(3)
        for _, row in benzerler_df.iterrows():
            sub = row["Suburb"] if "Suburb" in data.columns else BOLGE_MAP.get(row.get("Regionname", 0), "Bölge")
            benzer_evler.append({
                "suburb": sub,
                "price": float(row["Price"]),
                "distance": float(row["Distance"]),
                "bathroom": int(row["Bathroom"]),
                "car": int(row["Car"]),
                "type": "Müstakil" if row["Type"] == 0 else ("Sıra Ev" if row["Type"] == 1 else "Daire")
            })

    return {
        "total_matches": len(filtered),
        "top_3": top_3,
        "histogram": hist_data,
        "room_prices": oda_fiyat,
        "compare_options": compare_options,
        "map_data": map_data,
        "top_mahalleler": top_mahalleler,
        "benzer_evler": benzer_evler,
        "budget_mid": min_price + (max_price - min_price) * 0.5
    }

def get_market_data():
    if data.empty:
        return {}
        
    # 1. Bölge Özeti
    bolge_ozet = data.groupby("Regionname").agg(
        medyan_fiyat=("Price","median"), 
        ort_uzaklik=("Distance","mean"),
        ev_sayisi=("Price","count")
    ).reset_index()
    bolge_ozet["Bolge_Ismi"] = bolge_ozet["Regionname"].map(BOLGE_MAP)
    bolge_data = bolge_ozet.to_dict(orient="records")

    # 2. Yıllık Trend
    trend_data = data.copy()
    trend_data["Date"] = pd.to_datetime(trend_data["Date"], dayfirst=True, errors="coerce")
    trend_data = trend_data.dropna(subset=["Date"])
    trend_data["Yil"] = trend_data["Date"].dt.year
    yillik = trend_data.groupby("Yil")["Price"].median().reset_index()
    trend_list = yillik.to_dict(orient="records")
    
    # 3. Model Performansı
    return {
        "bolge_data": bolge_data,
        "trend_data": trend_list,
        "total_houses": len(data)
    }
