import streamlit as st
import numpy as np
import requests
import time

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
    payload = {
        "nama": nama,
        "nip": nip,
        "theta": round(theta, 4),
        "rel": round(rel, 4),
        "sem": round(sem, 4),
        "skor_akhir": skor
    }
    try:
        requests.post(url_script, json=payload)
        return True
    except:
        return False
if 'bank_soal' not in st.session_state or not st.session_state.bank_soal:
    st.session_state.bank_soal = ambil_bank_soal()
def hitung_prob_3pl(theta, a, b, c):
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))
def hitung_iif(theta, a, b, c):
    p = hitung_prob_3pl(theta, a, b, c)
    return (a**2) * ((1-p)/p) * ((p - c) / (1 - c))**2
def transform_ke_100(theta):
    theta_min, theta_max = -3.0, 3.0
    return round(((np.clip(theta, theta_min, theta_max) - theta_min) / (theta_max - theta_min)) * 100, 2)
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
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 20 - int(elapsed)) 
    c1, c2 = st.columns([3, 1])
    c1.title("🛡️ Tes CAT Online")
    c2.markdown(f"<div style='text-align:right'><b>👤 {st.session_state.nama}</b><br><span style='font-size:30px; color:{'red' if rem < 10 else 'black'}'>⏱️ {rem} Detik</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <style>
    /* Mengubah font seluruh aplikasi */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Mempercantik kotak pertanyaan (info box) */
    .stAlert {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: none;
        background-color: #f0f2f6;
    }
    
    /* Membuat tombol lebih modern */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #0056b3;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)
    # Tambahkan Progress Bar di bawah header
    progress = (st.session_state.index_soal) / len(st.session_state.bank_soal)
    st.progress(progress)

        if st.session_state.index_soal < len(st.session_state.bank_soal):
            if rem <= 0:
                st.session_state.index_soal += 1
                st.session_state.start_time = time.time()
                    st.rerun()
                sisa = [s for s in st.session_state.bank_soal if s['id'] not in [x['id'] for x in st.session_state.soal_selesai]]
                if not sisa: # Antisipasi jika soal habis
                     st.session_state.index_soal = len(st.session_state.bank_soal)
                     st.rerun()
                soal = min(sisa, key=lambda x: abs(x['b'] - st.session_state.theta))
                    st.subheader(f"Pertanyaan {st.session_state.index_soal + 1}")
                    st.info(soal['teks'])
                opsi_lengkap = [f"A. {soal['opsi_A']}", f"B. {soal['opsi_B']}", f"C. {soal['opsi_C']}", f"D. {soal['opsi_D']}"]
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
                time.sleep(1)
                    st.rerun()
            else:
                skor_akhir = transform_ke_100(st.session_state.theta)
                rel = st.session_state.total_info / (st.session_state.total_info + 1) if st.session_state.total_info > 0 else 0
                sem = 1 / np.sqrt(st.session_state.total_info) if st.session_state.total_info > 0 else 0
                    st.balloons()
                    st.success(f"Selamat {st.session_state.nama}, Anda telah menyelesaikan tes!")
                    st.metric(label="SKOR FINAL", value=f"{skor_akhir}")
                    if 'sent' not in st.session_state:
                        kirim_ke_sheets(st.session_state.nama, st.session_state.nip, st.session_state.theta, rel, sem, skor_akhir)
                        st.session_state.sent = True
                        st.info("Data telah dikirimkan ke PUSAT DATA PENILAIAN.")


