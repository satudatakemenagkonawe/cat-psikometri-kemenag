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
