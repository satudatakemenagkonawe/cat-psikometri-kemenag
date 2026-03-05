import streamlit as st
import numpy as np
import pandas as pd
import requests
import time

# --- 1. INISIALISASI SESSION STATE ---
if 'identitas_siap' not in st.session_state:
    st.session_state.identitas_siap = False
if 'index_soal' not in st.session_state:
    st.session_state.index_soal = 0
if 'theta' not in st.session_state:
    st.session_state.theta = 0.0
if 'soal_selesai' not in st.session_state:
    st.session_state.soal_selesai = []
if 'total_info' not in st.session_state:
    st.session_state.total_info = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

# --- 2. KONFIGURASI BANK SOAL ---
bank_soal = [
    {
        "id": 1, 
        "teks": "Dalam situasi konflik antar bawahan, tindakan pertama Anda adalah...",
        "opsi": ["A. Membiarkan mereka", "B. Memanggil kedua belah pihak", "C. Melapor ke atasan", "D. Memberi sanksi"],
        "kunci": "B",
        "a": 0.15, "b": 0.45, "c": 0.15, "D": 0.25  # Soal Mudah, Daya Beda Tinggi
    },
    {
        "id": 2, 
        "teks": "Bagaimana cara Anda menyikapi perubahan mendadak dalam prosedur kerja?",
        "opsi": ["A. Menolak", "B. Mengikuti saja", "C. Mempelajari dan beradaptasi", "D. Mengeluh"],
        "kunci": "C",
        "a": 0.20, "b": 0.30, "c": 0.40, "D": 0.10  # Soal Menengah-Mudah
    },
    {
        "id": 3, 
        "teks": "Prioritas utama dalam memberikan pelayanan publik menurut Anda adalah...",
        "opsi": ["A. Kecepatan", "B. Kepuasan pelanggan", "C. Prosedur formal", "D. Kenyamanan petugas"],
        "kunci": "B",
        "a": 0.20, "b": 0.50, "c": 0.10, "c": 0.10   # Soal Menengah-Sulit, Sangat Diskriminatif
    },
    {
        "id": 4, 
        "teks": "Menghadapi rekan kerja yang berasal dari latar belakang budaya berbeda, Anda akan...",
        "opsi": ["A. Bersikap acuh", "B. Menghargai perbedaan", "C. Menghindari", "D. Meminta pindah divisi"],
        "kunci": "B",
        "a": 0.15, "b": 0.55, "c": 0.20, "c": 0.10   # Soal Sedang
    },
    {
        "id": 5, 
        "teks": "Strategi paling efektif untuk mencapai target organisasi jangka panjang adalah...",
        "opsi": ["A. Inovasi berkelanjutan", "B. Mengurangi biaya", "C. Bekerja keras", "D. Menambah personil"],
        "kunci": "A",
        "a": 0.60, "b": 0.10, "c": 0.15, "c": 0.15   # Soal Sulit, Daya Beda Sangat Tinggi
    }
]
# --- 3. FUNGSI PSIKOMETRI & TRANSFORMASI ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

def transform_ke_500(theta):
    theta_min, theta_max = -3.0, 3.0
    theta_clipped = np.clip(theta, theta_min, theta_max)
    return round(((theta_clipped - theta_min) / (theta_max - theta_min)) * 500, 2)

def kirim_ke_sheets(nama, nip, theta, rel, sem, skor):
    url_script = "https://script.google.com/macros/s/AKfycbzugHdf8FJymxPrj0ymluwUAqd-PomZ7WEf29lbsF-RSt5Z4yId3AFqS6wckqgWf-Y0Lg/exec" # Pastikan URL ini benar
    
    # Payload harus sesuai dengan variabel yang dipanggil di Apps Script (data.nama, data.nip, dll)
    payload = {
        "nama": nama,
        "nip": nip,          # Ini akan masuk ke kolom Nomor_Peserta
        "theta": round(theta, 4),
        "rel": round(rel, 4),
        "sem": round(sem, 4),
        "skor_akhir": skor   # Ini mengirim nilai 0-300
    }
    
    try:
        response = requests.post(url_script, json=payload)
        return response.status_code == 500
    except:
        return False

# --- TAMPILAN ANTARMUKA ---
# Membuat header dengan 2 kolom: satu untuk judul, satu untuk info peserta
col_judul, col_info = st.columns([3, 1])

with col_judul:
    st.title("🛡️ Tes CAT Online")

with col_info:
    # Menghitung waktu di sini agar sinkron
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 60 - int(elapsed_time))
    
    # Menampilkan Nama dan Timer di pojok kanan atas
    st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <b>👤 {st.session_state.nama}</b><br>
            <span style="color: {'red' if remaining_time < 10 else 'black'}; font-size: 20px; font-weight: bold;">
                ⏱️ {remaining_time} Detik
            </span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---") # Garis pemisah header

if st.session_state.index_soal < len(bank_soal):
    # Logika Timer Otomatis (Tetap sama)
    if remaining_time <= 0:
        st.warning("Waktu habis!")
        # ... (logika pindah soal otomatis Anda) ...
else:
    if st.session_state.index_soal < len(bank_soal):
        # LOGIKA TIMER 60 DETIK
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = max(0, 60 - int(elapsed_time))
        
        if remaining_time <= 0:
            st.warning("Waktu habis! Berlanjut ke soal berikutnya...")
            time.sleep(1)
            st.session_state.index_soal += 1
            st.session_state.start_time = time.time()
            st.rerun()

        # Pemilihan Soal Adaptive
        sisa = [s for s in bank_soal if s['id'] not in [x['id'] for x in st.session_state.soal_selesai]]
        soal = min(sisa, key=lambda x: abs(x['b'] - st.session_state.theta))
        
        st.subheader(f"Pertanyaan {st.session_state.index_soal + 1}")
        st.info(soal['teks'])
        pilihan = st.radio("Pilih jawaban Anda:", soal['opsi'], index=None)
        
        if st.button("Simpan & Lanjutkan"):
            if pilihan:
                skor_biner = 1 if pilihan.startswith(soal['kunci']) else 0
                # Update IRT
                info = hitung_iif(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                st.session_state.total_info += info
                p = hitung_prob_3pl(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                st.session_state.theta += (0.85 * soal['a'] * ((skor_biner - p) / (1 - soal['c'])))
                
                st.session_state.soal_selesai.append(soal)
                st.session_state.index_soal += 1
                st.session_state.start_time = time.time() # Reset waktu untuk soal berikutnya
                st.rerun()
            else:
                st.warning("Silakan pilih jawaban sebelum melanjutkan.")
        
        # Refresh halaman setiap 1 detik untuk update timer
        time.sleep(1)
        st.rerun()

    else:
        # --- HALAMAN HASIL AKHIR ---
        skor_final = transform_ke_100(st.session_state.theta)
        rel = st.session_state.total_info / (st.session_state.total_info + 1)
        sem = 1 / np.sqrt(st.session_state.total_info) if st.session_state.total_info > 0 else 0
        
        st.balloons()
        st.success(f"Selamat {st.session_state.nama}, Anda telah menyelesaikan tes!")
        
        # HANYA TAMPILKAN SKOR 0-100
        st.markdown("### Hasil Evaluasi Anda:")
        st.metric(label="SKOR AKHIR", value=f"{skor_final}")
        
        # Kirim semua data (termasuk theta & rel) ke Sheets secara diam-diam
        if 'sent' not in st.session_state:
            kirim_ke_sheets(st.session_state.nama, st.session_state.nip, st.session_state.theta, rel, sem, skor_final)
            st.session_state.sent = True
        
        st.info("SELAMAT... Data detail hasil tes telah dikirimkan ke PUSAT DATA PENILAIAN.")







