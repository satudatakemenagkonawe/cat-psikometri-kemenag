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
    
# --- 2. KONFIGURASI BANK SOAL ---
bank_soal = [
    {"id": 1, "teks": "Dalam situasi konflik antar bawahan...", "opsi": ["A", "B", "C", "D"], "kunci": "B", "a": 1.65, "b": -1.20, "c": 0.22},
    {"id": 2, "teks": "Menyikapi perubahan mendadak...", "opsi": ["A", "B", "C", "D"], "kunci": "C", "a": 1.40, "b": -0.40, "c": 0.20},
    {"id": 3, "teks": "Prioritas pelayanan publik...", "opsi": ["A", "B", "C", "D"], "kunci": "B", "a": 1.90, "b": 0.60, "c": 0.18},
    {"id": 4, "teks": "Rekan kerja beda budaya...", "opsi": ["A", "B", "C", "D"], "kunci": "B", "a": 1.25, "b": 0.10, "c": 0.25},
    {"id": 5, "teks": "Strategi target organisasi...", "opsi": ["A", "B", "C", "D"], "kunci": "A", "a": 2.10, "b": 1.45, "c": 0.15}
]

# --- 3. FUNGSI PENDUKUNG ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

def transform_ke_100(theta):
    theta_min, theta_max = -3.0, 3.0
    theta_clipped = np.clip(theta, theta_min, theta_max)
    return round(((theta_clipped - theta_min) / (theta_max - theta_min)) * 100, 2)

# --- FUNGSI AMBIL SOAL DARI GOOGLE SHEETS ---
@st.cache_data(ttl=600) # Simpan di memori selama 10 menit agar tidak terus-menerus memanggil API
def ambil_bank_soal():
    url_script = "URL_WEB_APP_APPS_SCRIPT_ANDA"
    try:
        response = requests.get(url_script)
        if response.status_code == 200:
            return response.json()
    except:
        return []
# --- DI DALAM LOGIKA APLIKASI ---
if 'bank_soal' not in st.session_state or not st.session_state.bank_soal:
    data_soal = ambil_bank_soal()
    if data_soal:
        st.session_state.bank_soal = data_soal

# --- 4. LOGIKA HALAMAN ---
if not st.session_state.identitas_siap:
    # HALAMAN LOGIN
    st.title("🛡️ Tes CAT Online")
    with st.form("identitas"):
        st.subheader("Data Diri Peserta")
        nama = st.text_input("Nama Lengkap")
        nip = st.text_input("NIP / Nomor Pegawai")
        if st.form_submit_button("Mulai Tes"):
            if nama and nip:
                st.session_state.nama, st.session_state.nip = nama, nip
                st.session_state.identitas_siap = True
                st.session_state.start_time = time.time()
                st.rerun()
            else: st.error("Mohon lengkapi data diri.")
else:
    # --- HEADER DINAMIS ---
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 60 - int(elapsed_time))
    
    col_judul, col_info = st.columns([3, 1])
    with col_judul:
        st.title("🛡️ Tes CAT Online")
    with col_info:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 10px;">
                <b>👤 {st.session_state.nama}</b><br>
                <span style="color: {'red' if remaining_time < 10 else 'black'}; font-size: 20px; font-weight: bold;">
                    ⏱️ {remaining_time} Detik
                </span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # --- LOGIKA SOAL VS HASIL ---
    if st.session_state.index_soal < len(bank_soal):
        # CEK TIMER
        if remaining_time <= 0:
            st.warning("Waktu habis! Pindah ke soal berikutnya...")
            time.sleep(1)
            st.session_state.index_soal += 1
            st.session_state.start_time = time.time()
            st.rerun()

        # TAMPILKAN SOAL
        sisa = [s for s in bank_soal if s['id'] not in [x['id'] for x in st.session_state.soal_selesai]]
        soal = min(sisa, key=lambda x: abs(x['b'] - st.session_state.theta))
        
        st.subheader(f"Pertanyaan {st.session_state.index_soal + 1}")
        st.info(soal['teks'])
        pilihan = st.radio("Pilih jawaban:", soal['opsi'], index=None)
        
        if st.button("Simpan & Lanjutkan"):
            if pilihan:
                skor_biner = 1 if pilihan.startswith(soal['kunci']) else 0
                info = hitung_iif(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                st.session_state.total_info += info
                p = hitung_prob_3pl(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                st.session_state.theta += (0.85 * soal['a'] * ((skor_biner - p) / (1 - soal['c'])))
                
                st.session_state.soal_selesai.append(soal)
                st.session_state.index_soal += 1
                st.session_state.start_time = time.time()
                st.rerun()
            else: st.warning("Pilih jawaban dulu.")
        
        time.sleep(1)
        st.rerun()
    else:
        # HALAMAN HASIL
        skor_final = transform_ke_100(st.session_state.theta)
        rel = st.session_state.total_info / (st.session_state.total_info + 1)
        sem = 1 / np.sqrt(st.session_state.total_info) if st.session_state.total_info > 0 else 0
        
        st.balloons()
        st.success(f"Selamat {st.session_state.nama}, Anda telah menyelesaikan tes!")
        st.metric(label="SKOR AKHIR", value=f"{skor_final}")
        
        if 'sent' not in st.session_state:
            kirim_ke_sheets(st.session_state.nama, st.session_state.nip, st.session_state.theta, rel, sem, skor_final)
            st.session_state.sent = True
        st.info("Data telah dikirimkan ke PUSAT DATA PENILAIAN.")
        






