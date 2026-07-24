# CUKUPIN — Prototipe MVP

Prototipe aplikasi pencatatan & prediksi keuangan berbasis AI, dibuat untuk
memenuhi Bagian 3 (Tangkapan Artefak Kode & Prototipe MVP) — Analisis Design
Sprint.

## Fitur yang Didemokan
- **AI Prediksi Tanggal Uang Habis** — burn rate forecasting dari histori transaksi
- **AI Deteksi Kebiasaan Boros** — deteksi kategori pengeluaran yang tidak wajar
- **AI Goal Planner** — rekomendasi tabungan personal (opsional pakai Claude API)

## Cara Menjalankan Secara Lokal

```bash
git clone <link-repo-kamu>
cd cukupin-mvp
pip install -r requirements.txt
streamlit run app.py
```

Buka browser di `http://localhost:8501`.

## Cara Push ke GitHub (dari Nol)

1. Buat repository baru di [github.com/new](https://github.com/new), beri nama
   misalnya `cukupin-mvp`. Jangan centang "Add README" (karena sudah ada).
2. Di folder project ini, jalankan:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: CUKUPIN MVP prototype"
   git branch -M main
   git remote add origin https://github.com/<username>/cukupin-mvp.git
   git push -u origin main
   ```
3. Link repository ini yang kamu lampirkan di laporan.

## Cara Deploy ke Streamlit Community Cloud (Gratis)

1. Pastikan repo sudah di-push ke GitHub (langkah di atas).
2. Buka [share.streamlit.io](https://share.streamlit.io), login pakai akun GitHub.
3. Klik **"New app"** → pilih repository `cukupin-mvp` → branch `main` →
   file utama `app.py`.
4. Klik **Deploy**. Tunggu beberapa menit hingga aplikasi live.
5. Kamu akan dapat link seperti `https://cukupin-mvp.streamlit.app` — inilah
   link yang kamu lampirkan sebagai "Link Streamlit" di laporan.

> Catatan: fitur "Generate rekomendasi AI" butuh Anthropic API key yang
> diinput langsung di aplikasi (tidak disimpan di kode), jadi aman untuk
> di-deploy publik tanpa membocorkan API key kamu.

## Integrasi OCR (Lanjutan — Opsional)

Prototipe ini masih pakai input manual/CSV sebagai pengganti sementara OCR.
Untuk menyambungkan ke Google Cloud Vision API:

```python
from google.cloud import vision

def extract_text_from_screenshot(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    return response.text_annotations[0].description if response.text_annotations else ""
```

Hasil teks ini kemudian bisa diparse (regex/LLM) untuk diubah menjadi baris
transaksi (tanggal, nominal, kategori) sebelum masuk ke pipeline analisis
yang sudah ada di `app.py`.

## Struktur Project

```
cukupin-mvp/
├── app.py                       # Aplikasi Streamlit utama
├── requirements.txt             # Dependencies Python
├── data/
│   └── sample_transactions.csv  # Data dummy untuk demo
└── README.md
```
