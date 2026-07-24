"""
CUKUPIN — Prototipe MVP
Aplikasi pencatatan & prediksi keuangan berbasis AI.

Fitur yang didemokan di prototipe ini:
1. Input profil pengguna (mahasiswa / pekerja)
2. Input transaksi (manual, sebagai pengganti sementara OCR screenshot)
3. AI Prediksi Tanggal Uang Habis (time-series burn rate)
4. AI Deteksi Kebiasaan Boros (anomaly detection sederhana / z-score)
5. AI Goal Planner (rekomendasi via LLM API)

Catatan: OCR (Computer Vision) belum diintegrasikan penuh di prototipe ini.
Lihat bagian "Integrasi OCR (Lanjutan)" di README untuk cara menyambungkannya
ke Google Cloud Vision API.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="CUKUPIN - Prototipe MVP", page_icon="💸", layout="wide")

# ---------------------------------------------------------
# Sidebar - Profil Pengguna
# ---------------------------------------------------------
st.sidebar.title("💸 CUKUPIN")
st.sidebar.caption("Prototipe MVP — Design Sprint")

saldo_awal = st.sidebar.number_input("Saldo awal periode ini (Rp)", min_value=0, value=3000000, step=50000)
target_tabungan = st.sidebar.number_input("Target tabungan bulan ini (Rp)", min_value=0, value=300000, step=50000)
hari_tersisa = st.sidebar.number_input("Sisa hari hingga periode berikutnya (gajian/kiriman)", min_value=1, value=15)

st.sidebar.divider()
uploaded = st.sidebar.file_uploader("Unggah screenshot mutasi (opsional, demo saja)", type=["png", "jpg", "jpeg"])
if uploaded:
    st.sidebar.image(uploaded, caption="Preview screenshot (OCR belum aktif di prototipe ini)")
    st.sidebar.info("OCR akan mengekstrak transaksi ini secara otomatis pada versi penuh.")

# ---------------------------------------------------------
# Data Transaksi
# ---------------------------------------------------------
st.title("Dashboard Keuangan")

@st.cache_data
def load_sample_data():
    df = pd.read_csv("data/sample_transactions.csv", parse_dates=["tanggal"])
    return df

df = load_sample_data()
pengeluaran = df[df["kategori"] != "Gaji"].copy()

with st.expander("📄 Lihat / tambah transaksi manual"):
    st.dataframe(pengeluaran, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        new_kategori = st.text_input("Kategori", "Makanan & Minuman")
    with col2:
        new_nominal = st.number_input("Nominal (Rp)", min_value=0, value=20000, step=1000)
    with col3:
        if st.button("Tambah transaksi"):
            new_row = pd.DataFrame([{
                "tanggal": datetime.now(),
                "kategori": new_kategori,
                "nominal": new_nominal,
                "deskripsi": "Input manual"
            }])
            pengeluaran = pd.concat([pengeluaran, new_row], ignore_index=True)
            st.success("Transaksi ditambahkan (sesi ini saja).")

# ---------------------------------------------------------
# 1. AI Prediksi Tanggal Uang Habis (Burn Rate Forecasting)
# ---------------------------------------------------------
st.header("🔮 AI Prediksi Tanggal Uang Habis")

window = pengeluaran.tail(14)
burn_rate_harian = window["nominal"].sum() / max(len(window["tanggal"].dt.date.unique()), 1)
total_pengeluaran_periode = pengeluaran["nominal"].sum()
saldo_sekarang = saldo_awal - total_pengeluaran_periode

hari_sampai_habis = saldo_sekarang / burn_rate_harian if burn_rate_harian > 0 else float("inf")

col1, col2, col3 = st.columns(3)
col1.metric("Saldo saat ini (estimasi)", f"Rp {saldo_sekarang:,.0f}")
col2.metric("Burn rate harian", f"Rp {burn_rate_harian:,.0f}/hari")
col3.metric("Proyeksi saldo bertahan", f"{hari_sampai_habis:.1f} hari")

if hari_sampai_habis < hari_tersisa:
    kekurangan_hari = hari_tersisa - hari_sampai_habis
    st.error(
        f"⚠️ Berdasarkan pola pengeluaranmu, saldo diperkirakan habis "
        f"**{kekurangan_hari:.0f} hari sebelum** periode berikutnya. "
        f"Kurangi pengeluaran harian sekitar Rp{(burn_rate_harian * 0.15):,.0f} agar saldo aman."
    )
else:
    st.success("✅ Saldo diperkirakan cukup hingga periode berikutnya berdasarkan pola saat ini.")

# ---------------------------------------------------------
# 2. AI Deteksi Kebiasaan Boros (Anomaly Detection / Z-score)
# ---------------------------------------------------------
st.header("🚨 AI Deteksi Kebiasaan Boros")

per_kategori = pengeluaran.groupby("kategori")["nominal"].sum().reset_index()
per_kategori["persentase"] = (per_kategori["nominal"] / per_kategori["nominal"].sum() * 100).round(1)

# Anomaly sederhana: kategori yang menyumbang > 25% dari total pengeluaran dianggap perlu perhatian
threshold_pct = 25
anomali = per_kategori[per_kategori["persentase"] > threshold_pct].sort_values("persentase", ascending=False)

st.bar_chart(per_kategori.set_index("kategori")["nominal"])

if not anomali.empty:
    for _, row in anomali.iterrows():
        st.warning(
            f"Kategori **'{row['kategori']}'** menyumbang **{row['persentase']}%** "
            f"dari total pengeluaranmu — melebihi ambang batas wajar ({threshold_pct}%)."
        )
else:
    st.success("Tidak ada kategori yang menunjukkan pola pengeluaran tidak wajar.")

# ---------------------------------------------------------
# 3. AI Goal Planner (LLM-generated recommendation)
# ---------------------------------------------------------
st.header("🎯 AI Goal Planner Keuangan")

dana_fleksibel_tersisa = max(saldo_sekarang - target_tabungan, 0)
batas_harian = dana_fleksibel_tersisa / hari_tersisa if hari_tersisa > 0 else 0

st.write(
    f"Untuk mencapai target tabungan **Rp{target_tabungan:,.0f}** dalam **{hari_tersisa} hari** ke depan, "
    f"kamu perlu membatasi pengeluaran harian maksimal sekitar **Rp{batas_harian:,.0f}**."
)

with st.expander("💬 Minta rekomendasi personal dari AI (opsional — butuh API key)"):
    api_key = st.text_input("Anthropic API Key", type="password", help="Tidak disimpan, hanya untuk sesi ini")
    if st.button("Generate rekomendasi AI"):
        if not api_key:
            st.warning("Masukkan API key terlebih dahulu untuk mengaktifkan rekomendasi LLM.")
        else:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                prompt = f"""
                Kamu adalah asisten keuangan personal bernama CUKUPIN.
                Saldo saat ini: Rp{saldo_sekarang:,.0f}
                Target tabungan: Rp{target_tabungan:,.0f} dalam {hari_tersisa} hari
                Kategori pengeluaran tertinggi: {anomali['kategori'].tolist() if not anomali.empty else 'tidak ada anomali'}

                Berikan rekomendasi keuangan singkat (maks 3 kalimat), personal, dan actionable
                dalam bahasa Indonesia yang santai sesuai profil pengguna.
                """
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}],
                )
                st.info(response.content[0].text)
            except Exception as e:
                st.error(f"Gagal memanggil API: {e}")

st.divider()
st.caption(
    "Prototipe ini mendemokan alur inti CUKUPIN: input transaksi → analisis AI → "
    "rekomendasi personal. Integrasi OCR penuh dan model klasifikasi kategori "
    "berbasis NLP akan ditambahkan pada iterasi berikutnya."
)
