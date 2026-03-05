import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests

# --- 1. INISIALISASI SESSION STATE (WAJIB DI ATAS) ---
if 'identitas_siap' not in st.session_state:
    st.session_state.identitas_siap = False
if 'index_soal' not in st.session_state:
    st.session_state.index_soal = 0
if 'theta' not in st.session_state:
    st.session_state.theta = 0.0
if 'riwayat_theta' not in st.session_state:
    st.session_state.riwayat_theta = [0.0]
if 'soal_selesai' not in st.session_state:
    st.session_state.soal_selesai = []
if 'total_info' not in st.session_state:
    st.session_state.total_info = 0

# --- 2. KONFIGURASI BANK SOAL ---
bank_soal = [
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
    {
        "id": 5, 
        "teks": "Strategi paling efektif untuk mencapai target organisasi jangka panjang adalah...",
        "opsi": ["A. Inovasi berkelanjutan", "B. Mengurangi biaya", "C. Bekerja keras", "D. Menambah personil"],
        "kunci": "A",
        "a": 2.10, "b": 1.45, "c": 0.15   # Soal Sulit, Daya Beda Sangat Tinggi
    }
]
# --- 3. FUNGSI PSIKOMETRI & DATA ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

def kirim_ke_sheets(nama, nip, theta, rel, sem):
    url_script = "https://script.google.com/macros/s/AKfycbw3200UW17UxYZNFEbAOxTT3uMjsdNNG_z2pJov9Z9skI586UlT_w6h_Pz8Sv4xOnmD/exec" # Ganti dengan URL hasil Deploy
    payload = {"nama": nama, "nip": nip, "theta": theta, "rel": rel, "sem": sem}
    try:
        requests.post(url_script, json=payload)
        return True
    except: return False

# --- 4. TAMPILAN ANTARMUKA ---
st.title("🚀 CAT Psikometri Kemenag Konawe")

if not st.session_state.identitas_siap:
    # --- HALAMAN FORMULIR ---
    with st.form("identitas"):
        st.subheader("Data Diri Peserta")
        nama = st.text_input("Nama Lengkap")
        nip = st.text_input("NIP / Nomor Pegawai")
        if st.form_submit_button("Mulai Simulasi"):
            if nama and nip:
                st.session_state.nama = nama
                st.session_state.nip = nip
                st.session_state.identitas_siap = True
                st.rerun()
            else: st.error("Mohon lengkapi data.")
else:
    # --- HALAMAN TES ---
    st.sidebar.write(f"👤 **{st.session_state.nama}** ({st.session_state.nip})")
    
    if st.session_state.index_soal < len(bank_soal):
        # Logika Pemilihan Soal (Adaptive b)
        sisa = [s for s in bank_soal if s['id'] not in [x['id'] for x in st.session_state.soal_selesai]]
        soal = min(sisa, key=lambda x: abs(x['b'] - st.session_state.theta))
        
        st.info(f"Pertanyaan {st.session_state.index_soal + 1}: {soal['teks']}")
        pilihan = st.radio("Pilih jawaban:", soal['opsi'])
        
        if st.button("Kirim Jawaban"):
            skor = 1 if pilihan.startswith(soal['kunci']) else 0
            
            # Update IRT 3PL
            info = hitung_iif(st.session_state.theta, soal['a'], soal['b'], soal['c'])
            st.session_state.total_info += info
            p = hitung_prob_3pl(st.session_state.theta, soal['a'], soal['b'], soal['c'])
            st.session_state.theta += (0.85 * soal['a'] * ((skor - p) / (1 - soal['c'])))
            
            st.session_state.riwayat_theta.append(st.session_state.theta)
            st.session_state.soal_selesai.append(soal)
            st.session_state.index_soal += 1
            st.rerun()
    else:
        # --- HALAMAN SELESAI ---
        st.success("Tes Selesai! Skor Anda sedang diproses...")
        rel = st.session_state.total_info / (st.session_state.total_info + 1)
        sem = 1 / np.sqrt(st.session_state.total_info)
        
        if 'sent' not in st.session_state:
            kirim_ke_sheets(st.session_state.nama, st.session_state.nip, st.session_state.theta, rel, sem)
            st.session_state.sent = True
            st.balloons()
            
        st.metric("Estimasi Kemampuan (θ)", f"{st.session_state.theta:.3f}")
        st.write(f"Reliabilitas Marginal: **{rel:.3f}**")

