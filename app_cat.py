import streamlit as st
import pandas as pd
import numpy as np
import requests
import uuid
import random
import datetime
import time

st.set_page_config(page_title="CAT Kemenag Konawe", layout="wide")

API_URL = "YOUR_GOOGLE_SCRIPT_URL"

# =============================
# SESSION SECURITY
# =============================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "tab_lock" not in st.session_state:
    st.session_state.tab_lock = True
else:
    st.error("Tes sudah terbuka di tab lain.")
    st.stop()

# =============================
# API FUNCTIONS
# =============================

def api_get_bank_soal():
    try:
        r = requests.get(API_URL + "?action=soal")
        return r.json()
    except:
        return []

def api_register(nama,nip,session):
    payload={
        "action":"register",
        "nama":nama,
        "nip":nip,
        "session":session
    }
    requests.post(API_URL,json=payload)

def api_save_answer(session,soal_id,jawaban,skor,theta):

    payload={
        "action":"jawaban",
        "session":session,
        "soal_id":soal_id,
        "jawaban":jawaban,
        "skor":skor,
        "theta":theta
    }

    requests.post(API_URL,json=payload)

def api_save_result(nama,nip,skor,kategori,theta,rel):

    payload={
        "action":"hasil",
        "nama":nama,
        "nip":nip,
        "skor":skor,
        "kategori":kategori,
        "theta":theta,
        "reliabilitas":rel
    }

    requests.post(API_URL,json=payload)

# =============================
# IRT FUNCTIONS
# =============================

def prob_3pl(theta,a,b,c):

    return c + (1-c)/(1+np.exp(-a*(theta-b)))

def info_item(theta,a,b,c):

    p=prob_3pl(theta,a,b,c)

    return (a**2)*((1-p)/p)*((p-c)/(1-c))**2

def skor_100(theta):

    return round(((np.clip(theta,-3,3)+3)/6)*100,2)

# =============================
# KATEGORI KOMPETENSI
# =============================

def kategori(nilai):

    if nilai>=85:
        return "Sangat Kompeten"
    elif nilai>=70:
        return "Kompeten"
    elif nilai>=60:
        return "Cukup Kompeten"
    elif nilai>=50:
        return "Kurang Kompeten"
    else:
        return "Sangat Tidak Kompeten"

# =============================
# LOAD SOAL
# =============================

@st.cache_data(ttl=600)
def load_soal():

    return api_get_bank_soal()

bank_soal = load_soal()

# =============================
# INIT STATE
# =============================

if "login" not in st.session_state:

    st.session_state.login=False

if "theta" not in st.session_state:

    st.session_state.theta=0

if "index" not in st.session_state:

    st.session_state.index=0

if "done" not in st.session_state:

    st.session_state.done=[]

if "info" not in st.session_state:

    st.session_state.info=0

if "start_time" not in st.session_state:

    st.session_state.start_time=None

# =============================
# LOGIN
# =============================

if not st.session_state.login:

    st.title("🛡️ CAT Kemenag Konawe")

    nama=st.text_input("Nama")
    nip=st.text_input("Nomor Peserta")

    if st.button("Mulai Tes"):

        if nama and nip:

            st.session_state.nama=nama
            st.session_state.nip=nip
            st.session_state.login=True
            st.session_state.start_time=datetime.datetime.utcnow().timestamp()

            api_register(nama,nip,st.session_state.session_id)

            st.rerun()

        else:

            st.warning("Isi data")

    st.stop()

# =============================
# TIMER SERVER
# =============================

durasi=60

elapsed=datetime.datetime.utcnow().timestamp()-st.session_state.start_time

sisa=max(0,durasi-int(elapsed))

col1,col2=st.columns([4,1])

col1.title("CAT Online")

col2.metric("Sisa Waktu",f"{sisa} detik")

# =============================
# PROGRESS
# =============================

total=len(bank_soal)

st.progress(st.session_state.index/total)

# =============================
# SELEKSI CAT RANDOMIZED
# =============================

if st.session_state.index < total:

    if sisa<=0:

        st.session_state.index+=1

        st.session_state.start_time=datetime.datetime.utcnow().timestamp()

        st.rerun()

    sisa_soal=[s for s in bank_soal if s['id'] not in [x['id'] for x in st.session_state.done]]

    kandidat=random.sample(sisa_soal,min(5,len(sisa_soal)))

    soal=min(kandidat,key=lambda x:abs(x['b']-st.session_state.theta))

    st.subheader(f"Soal {st.session_state.index+1}")

    st.info(soal['teks'])

    opsi=[

        f"A. {soal['opsi_A']}",
        f"B. {soal['opsi_B']}",
        f"C. {soal['opsi_C']}",
        f"D. {soal['opsi_D']}"
    ]

    pilihan=st.radio("Jawaban",opsi,index=None)

    if st.button("Simpan Jawaban"):

        if pilihan:

            benar=1 if pilihan.startswith(soal['kunci']) else 0

            p=prob_3pl(st.session_state.theta,soal['a'],soal['b'],soal['c'])

            st.session_state.theta += 0.85*soal['a']*((benar-p)/(1-soal['c']))

            st.session_state.info += info_item(st.session_state.theta,soal['a'],soal['b'],soal['c'])

            st.session_state.done.append(soal)

            st.session_state.index+=1

            api_save_answer(

                st.session_state.session_id,
                soal['id'],
                pilihan,
                benar,
                st.session_state.theta
            )

            st.session_state.start_time=datetime.datetime.utcnow().timestamp()

            st.rerun()

# =============================
# HASIL AKHIR
# =============================

else:

    skor=skor_100(st.session_state.theta)

    rel=st.session_state.info/(st.session_state.info+1)

    kat=kategori(skor)

    st.balloons()

    st.success("Tes selesai")

    st.metric("SKOR",skor)

    st.write("Kategori :",kat)

    api_save_result(

        st.session_state.nama,
        st.session_state.nip,
        skor,
        kat,
        st.session_state.theta,
        rel
    )

# =============================
# DASHBOARD ADMIN
# =============================

st.sidebar.title("Admin")

password=st.sidebar.text_input("Admin Password",type="password")

if password=="admin123":

    try:

        r=requests.get(API_URL+"?action=ranking")

        df=pd.DataFrame(r.json())

        st.sidebar.write("Ranking Peserta")

        st.sidebar.dataframe(df)

    except:

        st.sidebar.warning("Tidak bisa mengambil data")
