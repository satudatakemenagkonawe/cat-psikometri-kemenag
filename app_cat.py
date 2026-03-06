import streamlit as st
import numpy as np
import requests
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Tes CAT Online", layout="wide")

# --- CUSTOM CSS (Agar Tampilan Cantik & Profesional) ---
st.markdown("""
    <style>
    /* 1. Latar Belakang Utama */
    .stApp {
        background-color: #5a5c57;
    }

    /* 2. Efek Glassmorphism untuk Kontainer/Layar CAT */
    /* Ini akan otomatis teraplikasi pada elemen blok seperti form atau pendukungnya */
    .stForm, .stChatMessage, div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* 3. Gaya Tombol Putih dengan Bayangan Kuning 3D */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #ffffff;
        color: #2E7D32;
        font-weight: bold;
        font-size: 20px;
        height: 3.5em;
        border: none;
        box-shadow: 0px 8px 0px #f1c40f;
        transition: all 0.1s ease;
        margin-top: 10px;
    }

    /* Efek Hover (Kursor di atas tombol) */
    .stButton>button:hover {
        background-color: #fcfcfc;
        color: #1B5E20;
        box-shadow: 0px 8px 0px #f1c40f;
        border: none;
    }

    /* Efek Click (Tombol Membal/Pressed) */
    .stButton>button:active {
        box-shadow: 0px 2px 0px #f1c40f !important;
        transform: translateY(6px);
        transition: all 0.1s ease;
    }

    /* 4. Penyesuaian Teks agar Terbaca di Background Gelap */
    h1, h2, h3, p, label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Contoh penggunaan dalam layout
with st.container():
    st.markdown("### Layar Simulasi CAT")
    st.write("Silahkan tekan tombol di bawah untuk memulai.")
    st.button("Masuk ke Ruang Tes")

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
    url_script = "https://script.google.com/macros/s/AKfycbzJXP_5EZMX56yP38-qxW919cJPGOC0KnX_HEtyXyKKMILViO0OTdwtpGH81MBZ7042Ng/exec"
    try:
        response = requests.get(url_script)
        return response.json()
    except:
        return []

def kirim_ke_sheets(nama, nip, theta, rel, sem, skor):
    url_script = "https://script.google.com/macros/s/AKfycbzJXP_5EZMX56yP38-qxW919cJPGOC0KnX_HEtyXyKKMILViO0OTdwtpGH81MBZ7042Ng/exec"
    payload = {"nama": nama, "nip": nip, "theta": theta, "rel": rel, "sem": sem, "skor_akhir": skor}
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
    st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🛡️ Sistem CAT Kemenag Konawe</h1>", unsafe_allow_html=True)
    with st.columns([1, 2, 1])[1]:
        with st.form("login_form"):
            nama = st.text_input("Nama Lengkap")
            nip = st.text_input("Nomor Peserta / NIP")
            if st.form_submit_button("Masuk ke Ruang Tes"):
                if nama and nip and st.session_state.bank_soal:
                    st.session_state.nama, st.session_state.nip = nama, nip
                    st.session_state.identitas_siap = True
                    st.session_state.start_time = time.time()
                    st.rerun()
                else: st.error("Lengkapi data diri atau cek koneksi Bank Soal.")
else:
    # HEADER DENGAN TIMER
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 60 - int(elapsed))
    
    col_t, col_p = st.columns([3, 1])
    col_t.title("🛡️ CAT Online")
    col_p.markdown(f"<div style='text-align:right; border-left: 3px solid #2E7D32; padding-left: 10px;'><b>👤 {st.session_state.nama}</b><br><span style='font-size:25px; color:{'red' if rem < 10 else '#2E7D32'};'>⏱️ {rem} s</span></div>", unsafe_allow_html=True)
    
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
                skor_biner = 1 if pilihan.startswith(soal['kunci']) else 0
                st.session_state.total_info += hitung_iif(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                p = hitung_prob_3pl(st.session_state.theta, soal['a'], soal['b'], soal['c'])
                st.session_state.theta += (0.85 * soal['a'] * ((skor_biner - p) / (1 - soal['c'])))
                st.session_state.soal_selesai.append(soal)
                st.session_state.index_soal += 1
                st.session_state.start_time = time.time()
                st.rerun()
        
        time.sleep(1)
        st.rerun()
    else:
        # HASIL AKHIR
        skor = transform_ke_100(st.session_state.theta)
        st.balloons()
        st.success(f"Tes Selesai! Selamat, {st.session_state.nama}.")
        st.metric("SKOR FINAL ANDA", f"{skor}")
        
        if 'sent' not in st.session_state:
            rel = st.session_state.total_info / (st.session_state.total_info + 1) if st.session_state.total_info > 0 else 0
            sem = 1 / np.sqrt(st.session_state.total_info) if st.session_state.total_info > 0 else 0
            kirim_ke_sheets(st.session_state.nama, st.session_state.nip, st.session_state.theta, rel, sem, skor)
            st.session_state.sent = True
        st.info("Hasil telah dikirimkan secara otomatis ke Database Pusat Data Penilaian.")






