const { useState, useEffect } = React;

function App() {
    const [oda, setOda] = useState(3);
    const [alan, setAlan] = useState(120);
    const [mesafe, setMesafe] = useState(10);
    const [yas, setYas] = useState(5);
    const [fiyat, setFiyat] = useState(null);
    const [loading, setLoading] = useState(false);

    const hesapla = async () => {
        setLoading(true);
        const veri = {
            oda_sayisi: oda,
            metrekare: alan,
            bolge_id: mesafe,
            bina_yasi: yas,
            banyo_sayisi: 1,
            garaj_sayisi: 1,
            ev_tipi: 0,
            bolge_kodu: 2
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(veri)
            });
            const data = await response.json();
            setFiyat(data.tahmini_fiyat);
        } catch (error) {
            console.error(error);
            setFiyat("Hata");
        }
        setLoading(false);
    };

    return (
        <div className="container">
            <header className="header">
                <h1>Melbourne Ev Karar Asistanı</h1>
                <p>Makine öğrenmesi destekli, premium ev fiyat tahmin asistanı.</p>
            </header>

            <main className="grid-2">
                <section className="panel">
                    <div className="panel-title">
                        <div className="step-num">1</div>
                        <h3>Ev Özellikleri</h3>
                    </div>
                    
                    <div className="form-group">
                        <label>Oda Sayısı: <span style={{color: 'var(--color-brown-light)'}}>{oda}</span></label>
                        <input type="range" min="1" max="10" value={oda} onChange={e => setOda(Number(e.target.value))} />
                    </div>

                    <div className="form-group">
                        <label>Metrekare (m²):</label>
                        <input type="number" className="form-input" value={alan} onChange={e => setAlan(Number(e.target.value))} />
                    </div>

                    <div className="form-group">
                        <label>Merkeze Uzaklık (km):</label>
                        <input type="number" className="form-input" value={mesafe} onChange={e => setMesafe(Number(e.target.value))} />
                    </div>

                    <div className="form-group">
                        <label>Bina Yaşı (Yıl):</label>
                        <input type="number" className="form-input" value={yas} onChange={e => setYas(Number(e.target.value))} />
                    </div>

                    <button className="btn-primary" onClick={hesapla} disabled={loading}>
                        {loading ? "Hesaplanıyor..." : "Fiyatı Tahmin Et"}
                    </button>
                </section>

                <section className="panel">
                    <div className="panel-title">
                        <div className="step-num">2</div>
                        <h3>Tahmin Sonucu</h3>
                    </div>
                    
                    {loading && <div className="loader"></div>}
                    
                    {!loading && fiyat !== null && (
                        <div className="result-container" style={{ textAlign: 'center', padding: '2rem 0' }}>
                            <p style={{ fontSize: '1.2rem', color: 'var(--color-brown-light)', marginBottom: '1rem', fontWeight: '500' }}>Modelimizin tahmini:</p>
                            {typeof fiyat === 'number' && fiyat > 0 ? (
                                <h2 style={{ fontSize: '3.5rem', color: 'var(--color-brown-dark)', fontFamily: 'Playfair Display' }}>
                                    {fiyat.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} <span style={{fontSize: '2rem'}}>$</span>
                                </h2>
                            ) : (
                                <p style={{ color: 'red', fontWeight: 'bold' }}>Model yüklenemedi veya bir hata oluştu.</p>
                            )}
                        </div>
                    )}
                    
                    {!loading && fiyat === null && (
                        <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--color-tan)', fontSize: '1.1rem' }}>
                            <p>Tahmin için yandaki özellikleri doldurup<br/>butona tıklayın.</p>
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
