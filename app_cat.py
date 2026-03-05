import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CAT Psikometri Pro", layout="wide")

# --- ENGINE PSIKOMETRI ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

# --- DATA BANK SOAL ---
if 'bank_soal' not in st.session_state:
    st.session_state.bank_soal = [
    {
        "id": 1, 
        "teks": "Dalam situasi konflik antar bawahan, tindakan pertama Anda adalah...",
        "opsi": ["A. Membiarkan mereka", "B. Memanggil kedua belah pihak", "C. Melapor ke atasan", "D. Memberi sanksi"],
        "kunci": "B",
        "a": 1.65, "b": -1.20, "c": 0.22  # Soal Mudah, Daya Beda Tinggi
    },
    {
        "id": 2, 
        "teks": "Bagaimana cara Anda menyikapi perubahan mendadak dalam prosedur kerja?",
        "opsi": ["A. Menolak", "B. Mengikuti saja", "C. Mempelajari dan beradaptasi", "D. Mengeluh"],
        "kunci": "C",
        "a": 1.40, "b": -0.40, "c": 0.20  # Soal Menengah-Mudah
    },
    {
        "id": 3, 
        "teks": "Prioritas utama dalam memberikan pelayanan publik menurut Anda adalah...",
        "opsi": ["A. Kecepatan", "B. Kepuasan pelanggan", "C. Prosedur formal", "D. Kenyamanan petugas"],
        "kunci": "B",
        "a": 1.90, "b": 0.60, "c": 0.18   # Soal Menengah-Sulit, Sangat Diskriminatif
    },
    {
        "id": 4, 
        "teks": "Menghadapi rekan kerja yang berasal dari latar belakang budaya berbeda, Anda akan...",
        "opsi": ["A. Bersikap acuh", "B. Menghargai perbedaan", "C. Menghindari", "D. Meminta pindah divisi"],
        "kunci": "B",
        "a": 1.25, "b": 0.10, "c": 0.25   # Soal Sedang
    },
    ]

# --- STATE MANAGEMENT ---
if 'theta' not in st.session_state:
    st.session_state.theta = 0.0
    st.session_state.riwayat_theta = [0.0]
    st.session_state.soal_selesai = []
    st.session_state.index_soal = 0
    st.session_state.total_info = 0

# --- UI APP ---
st.title("🚀 Prototipe Aplikasi CAT Psikometri")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.index_soal < len(st.session_state.bank_soal):
        # Item Selection (Adaptive)
        sisa_soal = [s for s in st.session_state.bank_soal if s['id'] not in [x['id'] for x in st.session_state.soal_selesai]]
        soal_aktif = min(sisa_soal, key=lambda x: abs(x['b'] - st.session_state.theta))
        
        st.subheader(f"Pertanyaan ke-{st.session_state.index_soal + 1}")
        st.info(soal_aktif['teks'])
        
        pilihan = st.radio("Pilih Jawaban Anda:", soal_aktif['opsi'], key=f"soal_{soal_aktif['id']}")
        
        if st.button("Kirim Jawaban"):
            # Scoring
            skor = 1 if pilihan.startswith(soal_aktif['kunci']) else 0
            
            # Update Psikometri
            info_b = hitung_iif(st.session_state.theta, soal_aktif['a'], soal_aktif['b'], soal_aktif['c'])
            st.session_state.total_info += info_b
            
            p = hitung_prob_3pl(st.session_state.theta, soal_aktif['a'], soal_aktif['b'], soal_aktif['c'])
            st.session_state.theta += (0.85 * soal_aktif['a'] * ((skor - p) / (1 - soal_aktif['c'])))
            
            st.session_state.riwayat_theta.append(st.session_state.theta)
            st.session_state.soal_selesai.append(soal_aktif)
            st.session_state.index_soal += 1
            st.rerun()
    else:
        st.success("✅ Tes Selesai! Silakan lihat hasil analisis di samping.")
        if st.button("Ulangi Tes"):
            for key in st.session_state.keys(): del st.session_state[key]
            st.rerun()

with col2:
    st.subheader("Statistik Real-time")
    st.metric("Estimasi Kemampuan (θ)", f"{st.session_state.theta:.3f}")
    
    if st.session_state.total_info > 0:
        rel = st.session_state.total_info / (st.session_state.total_info + 1)
        sem = 1 / np.sqrt(st.session_state.total_info)
        st.write(f"**Reliabilitas Marginal:** {rel:.3f}")
        st.write(f"**SEM:** {sem:.3f}")

# --- GRAFIK ANALISIS ---
if st.session_state.index_soal > 0:
    st.markdown("---")
    st.subheader("Analisis Visual Performa")
    
    fig, ax = plt.subplots(1, 2, figsize=(15, 5))
    
    # Trajektori
    ax[0].plot(st.session_state.riwayat_theta, marker='o', color='teal')
    ax[0].set_title("Pergerakan Kemampuan (Theta)")
    ax[0].set_ylim(-4, 4)
    ax[0].grid(True, alpha=0.3)
    
    # ICC
    t_range = np.linspace(-4, 4, 100)
    for s in st.session_state.soal_selesai:
        p_range = hitung_prob_3pl(t_range, s['a'], s['b'], s['c'])
        ax[1].plot(t_range, p_range, alpha=0.5, label=f"b={s['b']}")
    ax[1].axvline(st.session_state.theta, color='red', linestyle='--')
    ax[1].set_title("Kurva Karakteristik Item (ICC)")
    
    st.pyplot(fig)