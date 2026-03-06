import streamlit as st
import numpy as np
import requests
import time

# --- 1. KONFIGURASI HALAMAN & STATE ---
st.set_page_config(page_title="Tes CAT Online", layout="wide")

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

# --- 2. FUNGSI AMBIL SOAL DINAMIS ---
@st.cache_data(ttl=60)
def ambil_bank_soal():
def simpan_ke_gsheet(hasil_data):
    url_script = "https://script.google.com/macros/s/AKfycbwRxsZQ8gJl8NTcgqb3axJ_LE3ioFGA5dpfK0pD4sWoi16h1yXKGtn36VVGuXQVn-YOtA/exec"
    try:
        response = requests.post(url_script, json=hasil_data)
        return response.text
    except Exception as e:
        return str(e)
        
# Load soal ke session state
if 'bank_soal' not in st.session_state or not st.session_state.bank_soal:
    st.session_state.bank_soal = ambil_bank_soal()

# --- 3. FUNGSI PSIKOMETRI ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

def transform_ke_100(theta):
    theta_min, theta_max = -3.0, 3.0
    return round(((np.clip(theta, theta_min, theta_max) - theta_min) / (theta_max - theta_min)) * 100, 2)

# --- 4. LOGIKA ANTARMUKA ---
if not st.session_state.identitas_siap:
    st.title("🛡️ Tes CAT Online")
    with st.form("login"):
        nama = st.text_input("Nama Lengkap")
        nip = st.text_input("Nomor Peserta")
        if st.form_submit_button("Mulai Tes"):
            if nama and nip and st.session_state.bank_soal:
                st.session_state.nama, st.session_state.nip = nama, nip
                st.session_state.identitas_siap = True
                st.session_state.start_time = time.time()
                st.rerun()
            elif not st.session_state.bank_soal:
                st.error("Bank soal kosong. Periksa Google Sheets dan Apps Script Anda.")
            else: st.error("Lengkapi data diri.")
else:
    # HEADER KANAN ATAS
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 20 - int(elapsed))
    
    c1, c2 = st.columns([3, 1])
    c1.title("🛡️ Tes CAT Online")
    c2.markdown(f"<div style='text-align:right'><b>👤 {st.session_state.nama}</b><br><span style='font-size:30px; color:{'red' if rem < 20 else 'black'}'>⏱️ {rem} Detik</span></div>", unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.index_soal < len(st.session_state.bank_soal):
        if rem <= 0:
            st.session_state.index_soal += 1
            st.session_state.start_time = time.time()
            st.rerun()

        # Adaptive Selection
        sisa = [s for s in st.session_state.bank_soal if s['id'] not in [x['id'] for x in st.session_state.soal_selesai]]
        soal = min(sisa, key=lambda x: abs(x['b'] - st.session_state.theta))
        
        st.subheader(f"Pertanyaan {st.session_state.index_soal + 1}")
        st.info(soal['teks'])
        
        # Opsi jawaban dari kolom opsi_A sampai opsi_D
        opsi_lengkap = [
            f"A. {soal['opsi_A']}",
            f"B. {soal['opsi_B']}",
            f"C. {soal['opsi_C']}",
            f"D. {soal['opsi_D']}"
        ]
        pilihan = st.radio("Pilih jawaban Anda:", opsi_lengkap, index=None)
        
        if st.button("Simpan & Lanjutkan"):
            if pilihan:
                skor_biner = 1 if pilihan.startswith(soal['kunci']) else 0
                st.session_state.total_info += hitung_iif(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                p = hitung_prob_3pl(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                st.session_state.theta += (0.85 * soal['a'] * ((skor_biner - p) / (1 - soal['c'])))
                st.session_state.soal_selesai.append(soal)
                st.session_state.index_soal += 1
                st.session_state.start_time = time.time()
                st.rerun()
        # Contoh saat tombol 'Selesai' diklik atau soal habis
        if st.button("Selesai Tes"):
            data_untuk_dikirim = {
            "nama": st.session_state.nama_user,
            "nip": st.session_state.nip_user,
            "theta": st.session_state.theta_akhir,
            "rel": st.session_state.reliabilitas,
            "sem": st.session_state.sem_akhir,
            "skor_akhir": st.session_state.skor_0_100
        }
    
        status = simpan_ke_gsheet(data_untuk_dikirim)
        if status == "Sukses":
            st.success("Data berhasil disimpan ke Google Sheet!")
        else:
            st.error(f"Gagal menyimpan: {status}")
            time.sleep(1)
            st.rerun()
        else:
            st.success(f"Tes Selesai! Skor Akhir Anda: {transform_ke_100(st.session_state.theta)}")
            st.balloons()
            st.info("SELAMAT... Data detail hasil tes telah dikirim ke PUSAT DATA PENILAIAN.")        




