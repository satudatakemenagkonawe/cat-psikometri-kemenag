import streamlit as st
import requests
import numpy as np
import math
import time
import uuid

st.set_page_config(page_title="CAT Online", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbwtdEei5DFD95dlEvegxqS1oorA7Nr1H44k2s6SqysuvomcSH119cbV04gvt40h5A_qrA/exec"

MAX_SOAL = 30 # Batas jumlah soal
TIME_LIMIT = 60

# ======================================
# 1. CENTRALIZED SESSION INITIALIZER
# ======================================
# Taruh ini di paling atas agar variabel selalu ada sebelum dipanggil baris lain
if "initialized" not in st.session_state:
    st.session_state.theta = 0.0
    st.session_state.responses = []
    st.session_state.items_history = [] # Gunakan satu nama yang konsisten
    st.session_state.index = 0
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.start_time = time.time()
    st.session_state.initialized = True

# =====================
# 2. LOAD BANK SOAL
# =====================
@st.cache_data(ttl=300)
def load_bank():
    try:
        r = requests.get(API_URL)
        data = r.json()
        for i in data:
            i["a"] = float(i["a"])
            i["b"] = float(i["b"])
            i["c"] = float(i["c"])
        return data
    except Exception as e:
        st.error(f"Gagal memuat bank soal: {e}")
        return []

# =====================
# 3. IRT & CAT LOGIC
# =====================
def prob(theta, a, b, c):
    return c + (1 - c) / (1 + math.exp(-a * (theta - b)))

def information(theta, a, b, c):
    p = prob(theta, a, b, c)
    q = 1 - p
    if p <= 1e-9 or q <= 1e-9: return 0
    return (a**2 * (p - c)**2) / ((1 - c)**2 * p * q)

def select_next_item(theta, bank, used_ids):
    best_item = None
    max_info = -1
    for item in bank:
        if item["id"] in used_ids:
            continue
        info = information(theta, item["a"], item["b"], item["c"])
        if info > max_info:
            max_info = info
            best_item = item
    return best_item

def update_theta_simple(theta, responses):
    # Logika sederhana: naik/turun berdasarkan jawaban terakhir
    # Ganti dengan MLE jika Anda sudah memiliki rumusnya
    if not responses: return theta
    last_res = responses[-1]
    step = 0.4 if last_res == 1 else -0.4
    return np.clip(theta + step, -3.0, 3.0)

def get_score(theta):
    return round(((np.clip(theta, -3, 3) + 3) / 6) * 100, 2)

# =====================
# 4. ALUR APLIKASI
# =====================
bank = load_bank()

# LOGIN SCREEN
if "nama" not in st.session_state:
    st.title("Login CAT")
    nama = st.text_input("Nama")
    nip = st.text_input("Nomor Peserta")
    if st.button("Mulai Tes"):
        if nama and nip:
            st.session_state.nama = nama
            st.session_state.nip = nip
            st.session_state.start_time = time.time()
            st.rerun()
        else:
            st.warning("Isi nama dan nomor peserta!")
    st.stop()

# TEST SCREEN
elapsed = time.time() - st.session_state.start_time
sisa_waktu = max(0, TIME_LIMIT - int(elapsed))

if st.session_state.index >= MAX_SOAL or sisa_waktu <= 0:
    st.success("Tes Selesai!")
    final_score = get_score(st.session_state.theta)
    st.metric("Skor Akhir", final_score)
    # Tampilkan tombol restart jika perlu
    if st.button("Ulangi Tes"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# Ambil ID yang sudah digunakan
used_ids = [x["id"] for x in st.session_state.items_history]
soal_saat_ini = select_next_item(st.session_state.theta, bank, used_ids)

if soal_saat_ini:
    st.title("CAT Online")
    cols = st.columns(2)
    cols[0].write(f"**Peserta:** {st.session_state.nama}")
    cols[1].write(f"**Sisa Waktu:** {sisa_waktu} detik")
    
    st.divider()
    st.subheader(f"Soal ke-{st.session_state.index + 1}")
    st.write(soal_saat_ini["teks"])

    opsi = [
        f"A. {soal_saat_ini['opsi_A']}",
        f"B. {soal_saat_ini['opsi_B']}",
        f"C. {soal_saat_ini['opsi_C']}",
        f"D. {soal_saat_ini['opsi_D']}"
    ]

    pilih = st.radio("Pilih Jawaban:", opsi, index=None)

    if st.button("Simpan & Lanjut"):
        if pilih:
            # Hitung skor (cek apakah huruf awal pilihan sesuai kunci)
            is_correct = 1 if pilih.startswith(soal_saat_ini["kunci"]) else 0
            
            # Simpan history
            st.session_state.responses.append(is_correct)
            st.session_state.items_history.append(soal_saat_ini)
            
            # Update kemampuan (theta)
            st.session_state.theta = update_theta_simple(
                st.session_state.theta, 
                st.session_state.responses
            )
            
            # Progres ke soal berikutnya
            st.session_state.index += 1
            st.session_state.start_time = time.time() # Reset timer per soal jika perlu
            st.rerun()
        else:
            st.error("Pilih jawaban terlebih dahulu!")
else:
    st.error("Bank soal habis atau tidak ditemukan.")
