async function fiyatTahminEt() {
    // Formdan verileri alıyoruz
    const veri = {
        oda_sayisi: Number(document.getElementById('oda').value),
        metrekare: Number(document.getElementById('alan').value),
        bolge_id: Number(document.getElementById('bolge').value),
        bina_yasi: Number(document.getElementById('yas').value)
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(veri)
        });

        const sonuc = await response.json();
        console.log("Sunucudan Gelen Ham Veri:", sonuc);

        // Python tarafında "tahmini_fiyat" ismini kullandık
        let fiyat = sonuc.tahmini_fiyat;

        // Eğer hala gelmiyorsa, objenin içindeki ilk sayısal değeri bulmaya çalışalım
        if (fiyat === undefined || fiyat === null) {
            fiyat = Object.values(sonuc).find(v => typeof v === 'number');
        }

        if (fiyat !== undefined) {
            // Sayıyı formatla ve ekrana yaz
            const formatli = Number(fiyat).toLocaleString('tr-TR', { maximumFractionDigits: 0 });
            document.getElementById('sonuc').innerText = "Tahmin Edilen Fiyat: " + formatli + " $";
        } else {
            document.getElementById('sonuc').innerText = "Hata: Tahmin verisi okunamadı.";
        }

    } catch (error) {
        console.error("Hata detayı:", error);
        document.getElementById('sonuc').innerText = "Bağlantı Hatası!";
    }
}