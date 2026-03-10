import streamlit as st
import numpy as np
import requests
import json
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Tes CAT Online", layout="wide")

import streamlit as st

# --- CUSTOM CSS (Tampilan Profesional & Glassmorphism) ---
st.markdown("""
    <style>
    /* 1. Mengatur Latar Belakang Utama */
    .stApp {
        background-color: #5a5c57;
    }

    /* 2. Efek Glassmorphism (Kaca Buram) untuk Layar CAT */
    /* Gunakan kontainer ini untuk membungkus elemen form/text */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    /* 3. Gaya Tombol Putih dengan Bayangan Kuning (Persis Gambar Pertama) */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #1a4d2e;    /* Warna Teks Hijau Tua */
        color: #ffffff;               /* Warna Putih */
        font-weight: bold;
        font-size: 20px;
        height: 3.5em;
        border: none;
        
        /* Efek Shadow Kuning 3D */
        box-shadow: 0px 8px 0px #f1c40f; 
        transition: all 0.1s ease;
    }

    /* Efek Hover (Saat kursor di atas tombol) */
    .stButton>button:hover {
        background-color: #1a4d2e;
        color: #1B5E20;
        box-shadow: 0px 8px 0px #f1c40f;
        border: none;
    }

    /* Efek Klik (Tombol Membal ke Bawah) */
    .stButton>button:active {
        box-shadow: 0px 2px 0px #f1c40f !important;
        transform: translateY(6px);
    }

    /* Penyesuaian warna teks standar agar putih (terbaca di bg gelap) */
    h1, h2, h3, p, label, .stMarkdown {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INISIALISASI STATE ---
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

# --- 3. FUNGSI AMBIL & KIRIM DATA ---
@st.cache_data(ttl=60)
def ambil_bank_soal():
    url_script = "https://script.google.com/macros/s/AKfycbxke_3b68jKV5u2EgpZ2-S7aNhmiq-XOvvRybpporTJWf4e_T1SY0aCRqR7nDduDLGMjg/exec"
    try:
        response = requests.get(url_script)
        return response.json()
    except:
        return []

def kirim_ke_sheets(nama, nip, theta, rel, sem, skor, jawaban_list):
    url_script = "URL_APPS_SCRIPT_ANDA" # Ganti dengan URL /exec terbaru
    payload = {
        "session_id": st.session_state.get('session_id', 'code01'),
        "nama": nama, 
        "nip": nip, 
        "theta": theta,
        "rel": rel, 
        "sem": sem, 
        "skor_akhir": skor,
        "jawaban": jawaban_list  # Mengirim List 25 jawaban
    }
    try:
        requests.post(url_script, json=payload)
    except:
        pass        

# Load Soal
if 'bank_soal' not in st.session_state or not st.session_state.bank_soal:
    st.session_state.bank_soal = ambil_bank_soal()

# --- 4. LOGIKA PSIKOMETRI ---
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2

def transform_ke_100(theta):
    return round(((np.clip(theta, -3, 3) + 3) / 6) * 100, 2)

# --- 5. ANTARMUKA ---
if not st.session_state.identitas_siap:
    
    # HALAMAN LOGIN
    st.markdown("<h1 style='text-align: center; color: #1a4d2e;'>🛡️ Sistem CAT Kemenag Konawe</h1>", unsafe_allow_html=True)
    with st.columns([1, 2, 1])[1]:
        with st.form("login_form"):
            nama = st.text_input("Nama Lengkap - HURUF BESAR TANPA GELAR")
            nip = st.text_input("NIP")
            if st.form_submit_button("Mulai Tes"):
                if nama and nip and st.session_state.bank_soal:
                    st.session_state.nama, st.session_state.nip = nama, nip
                    st.session_state.identitas_siap = True
                    st.session_state.start_time = time.time()
                    st.rerun()
                else: st.error("Lengkapi data diri atau cek koneksi Bank Soal.")
else:
    # HEADER DENGAN TIMER
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 20 - int(elapsed))
    
    col_t, col_p = st.columns([3, 1])
    col_t.title("🛡️ CAT Online")
    col_p.markdown(f"<div style='text-align:left; border-left: 3px solid #ffffff; padding-left: 10px;'><b>👤 {st.session_state.nama}</b><br><span style='font-size:40px; color:{'blue' if rem < 10 else '#ffffff'};'>⏱️ {rem} s</span></div>", unsafe_allow_html=True)
    
    st.progress(st.session_state.index_soal / len(st.session_state.bank_soal))

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
        
        opsi = [f"A. {soal['opsi_A']}", f"B. {soal['opsi_B']}", f"C. {soal['opsi_C']}", f"D. {soal['opsi_D']}"]
        pilihan = st.radio("Jawaban Anda:", opsi, index=None)
        
        if st.button("Simpan Jawaban & Lanjutkan"):
            if pilihan:
                # 1. CATAT JAWABAN (Untuk Google Sheets nanti)
                if 'jawaban_per_nomor' not in st.session_state:
                    st.session_state.jawaban_per_nomor = {}
        
                # Gunakan index_soal + 1 agar nomor soal di Sheet mulai dari 1, 2, 3...
                no_soal_saat_ini = st.session_state.index_soal + 1
                st.session_state.jawaban_per_nomor[no_soal_saat_ini] = pilihan[0]

                # 2. LOGIKA IRT/THETA (Dipertahankan untuk menghitung skor)
                skor_biner = 1 if pilihan.startswith(soal['kunci']) else 0
        
                # Menghitung Information Function (IIF)
                st.session_state.total_info += hitung_iif(st.session_state.theta, soal['a'], soal['b'], soal['c'])
        
                # Menghitung Probabilitas jawaban benar (3PL)
                p = hitung_prob_3pl(st.session_state.theta, soal['a'], soal['b'], soal['c'])
        
                # Update Kemampuan (Theta) peserta berdasarkan jawaban tadi
                st.session_state.theta += (0.85 * soal['a'] * ((skor_biner - p) / (1 - soal['c'])))
        
                # 3. MANAGEMENT STATE (Pindah ke soal berikutnya)
                st.session_state.soal_selesai.append(soal)
                st.session_state.index_soal += 1
                st.session_state.start_time = time.time() # Reset waktu untuk soal berikutnya
        
                st.rerun() # Refresh halaman untuk menampilkan soal baru
        
        time.sleep(1)
        st.rerun()
    else:
        # --- BAGIAN HASIL AKHIR ---
        if len(st.session_state.soal_selesai) >= 25:
            skor = transform_ke_100(st.session_state.theta)
                st.balloons()
                st.success(f"Tes Selesai! Selamat, {st.session_state.nama}.")
                st.metric("SKOR FINAL ANDA", f"{skor}")

        # Logika Pengiriman Otomatis (Hanya berjalan sekali berkat state 'sent')
        if 'sent' not in st.session_state:
        # 1. Hitung Reliabilitas dan SEM
            rel = st.session_state.total_info / (st.session_state.total_info + 1) if st.session_state.total_info > 0 else 0
            sem = 1 / np.sqrt(st.session_state.total_info) if st.session_state.total_info > 0 else 0
        
        # 2. SUSUN DAFTAR 25 JAWABAN (Logika Baru)
        # Mengambil jawaban dari nomor 1 sampai 25
        daftar_25_jawaban = [st.session_state.jawaban_per_nomor.get(i, "") for i in range(1, 26)]
        
        # 3. KIRIM KE SHEETS (Dengan parameter tambahan daftar_25_jawaban)
        try:
            kirim_ke_sheets(
                st.session_state.nama, 
                st.session_state.nip, 
                st.session_state.theta, 
                rel, 
                sem, 
                skor, 
                daftar_25_jawaban  # Pastikan fungsi kirim_ke_sheets sudah diupdate
            )
            st.session_state.sent = True
            st.info("Hasil dan pilihan jawaban telah dikirimkan secara otomatis ke Database Pusat.")
        except Exception as e:
            st.error(f"Gagal mengirim ke database: {e}")

