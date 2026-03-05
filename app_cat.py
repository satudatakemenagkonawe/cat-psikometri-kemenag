import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- INSIALISASI STATE (Wajib di bagian paling atas setelah import) ---
if 'identitas_siap' not in st.session_state:
    st.session_state.identitas_siap = False
if 'index_soal' not in st.session_state:
    st.session_state.index_soal = 0
if 'bank_soal' not in st.session_state:
    # Masukkan daftar soal Anda di sini
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
    {
        "id": 5, 
        "teks": "Strategi paling efektif untuk mencapai target organisasi jangka panjang adalah...",
        "opsi": ["A. Inovasi berkelanjutan", "B. Mengurangi biaya", "C. Bekerja keras", "D. Menambah personil"],
        "kunci": "A",
        "a": 2.10, "b": 1.45, "c": 0.15   # Soal Sulit, Daya Beda Sangat Tinggi
    }
]
# --- 1. HALAMAN IDENTITAS ---
if not st.session_state.identitas_siap:
    st.title("📝 Identitas Peserta Tes")
    with st.form("form_awal"):
        nama = st.text_input("Nama Lengkap")
        nip = st.text_input("NIP / Nomor Peserta")
        if st.form_submit_button("Mulai Tes"):
            if nama and nip:
                st.session_state.nama = nama
                st.session_state.nip = nip
                st.session_state.identitas_siap = True
                st.rerun()
            else:
                st.error("Mohon isi data diri terlebih dahulu.") 
                
# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Computer Adaptive Tesrting", layout="wide")

# --- FUNGSI KIRIM DATA (Google Apps Script) ---
def kirim_ke_google_sheets(nama, no_peserta, theta, rel, sem):
    # Tempelkan URL Web App dari Apps Script Anda di sini
    url_script = "https://script.google.com/macros/s/AKfycbw3200UW17UxYZNFEbAOxTT3uMjsdNNG_z2pJov9Z9skI586UlT_w6h_Pz8Sv4xOnmD/exec"
    
    payload = {
        "nama": nama,
        "no_peserta": no_peserta,
        "theta": round(theta, 4),
        "rel": round(rel, 4),
        "sem": round(sem, 4)
    }
    
    try:
        response = requests.post(url_script, json=payload)
        return response.status_code == 200
    except:
        return False

# --- FORMULIR IDENTITAS ---
if 'identitas_siap' not in st.session_state:
    st.session_state.identitas_siap = False

if not st.session_state.identitas_siap:
    st.title("📝 Identitas Peserta Tes")
    st.info("Silakan isi data diri Anda sebelum memulai TES.")
    
    with st.form("form_identitas"):
        nama_input = st.text_input("Nama Lengkap")
        no_peserta_input = st.text_input("Nomor peserta")
        
        submit_identitas = st.form_submit_button("Mulai Tes")
        
        if submit_identitas:
            if nama_peserta_input and no_peserta_input:
                st.session_state.nama_peserta = nama_peserta_input
                st.session_state.no_peserta = no_peserta_input
                st.session_state.identitas_siap = True
                st.rerun()
            else:
                st.warning("Mohon isi Nama dan NOMOR PESERTA terlebih dahulu.")
else:
    # --- LOGIKA TES ANDA (Yang sudah kita buat sebelumnya) ---
    st.sidebar.title("👤 Profil Peserta")
    st.sidebar.write(f"**Nama Peserta:** {st.session_state.nama}")
    st.sidebar.write(f"**Nomor Peserta:** {st.session_state.nip}")
    
# --- ENGINE PSIKOMETRI ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

# --- DATA BANK SOAL ---
if 'bank_soal' not in st.session_state:
    st.session_state.bank_soal = [

# Tambahkan ini di bagian akhir tes setelah soal ke-5 dijawab
if st.session_state.index_soal == len(st.session_state.bank_soal):
    st.success(f"Tes Selesai, {st.session_state.nama}!")
    
    # Menghitung statistik akhir
    rel = st.session_state.total_info / (st.session_state.total_info + 1)
    sem = 1 / np.sqrt(st.session_state.total_info)
    
    # Kirim data otomatis sekali saja
    if 'data_terkirim' not in st.session_state:
        berhasil = kirim_ke_google_sheets(
            st.session_state.nama, 
            st.session_state.nip, 
            st.session_state.theta, 
            rel, 
            sem
        )
        if berhasil:
            st.session_state.data_terkirim = True
            st.balloons()
            st.info("✅ Data Anda telah tercatat secara otomatis di database kantor.")

