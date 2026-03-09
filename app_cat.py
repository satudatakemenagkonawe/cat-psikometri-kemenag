import streamlit as st
import numpy as np
import requests
import time
import json
import math
import os

# ================================
# KONFIGURASI
# ================================

st.set_page_config(page_title="Tes CAT Online", layout="wide")

SESSION_FILE = "cat_session.json"

THETA_MIN = -4
THETA_MAX = 4

MAX_ITEMS = 30
SE_THRESHOLD = 0.30
EXPOSURE_LIMIT = 0.25

SERVER_TIME_LIMIT = 60


# ================================
# SESSION PERSISTENCE
# ================================

def load_session():

    if os.path.exists(SESSION_FILE):

        with open(SESSION_FILE,"r") as f:
            return json.load(f)

    return None


def save_session(data):

    safe_data = json.loads(json.dumps(data, default=str))

    with open(SESSION_FILE,"w") as f:
        json.dump(safe_data,f)

    saved = load_session()

    if saved:
        for k,v in saved.items():
            st.session_state[k] = v

# ================================
# AMBIL BANK SOAL
# ================================

@st.cache_data(ttl=60)
def ambil_bank_soal():

    url_script="https://script.google.com/macros/s/AKfycbzJXP_5EZMX56yP38-qxW919cJPGOC0KnX_HEtyXyKKMILViO0OTdwtpGH81MBZ7042Ng/exec"

    try:

        r=requests.get(url_script)

        return r.json()

    except:

        return []


# ================================
# KIRIM HASIL
# ================================

def kirim_ke_sheets(nama,nip,theta,rel,sem,skor):

    url_script="https://script.google.com/macros/s/AKfycbzJXP_5EZMX56yP38-qxW919cJPGOC0KnX_HEtyXyKKMILViO0OTdwtpGH81MBZ7042Ng/exec"

    payload={
        "nama":nama,
        "nip":nip,
        "theta":theta,
        "rel":rel,
        "sem":sem,
        "skor_akhir":skor
    }

    try:
        requests.post(url_script,json=payload)
    except:
        pass


# ================================
# IRT 3PL PROBABILITY
# ================================

def irt_probability(theta,a,b,c):

    return c + (1-c)/(1+math.exp(-a*(theta-b)))


# ================================
# ITEM INFORMATION
# ================================

def item_information(theta,a,b,c):

    p=irt_probability(theta,a,b,c)
    q=1-p

    if p==0 or q==0:
        return 0

    info=(a**2*(p-c)**2)/((1-c)**2*p*q)

    return info


# ================================
# PILIH SOAL (FISHER INFORMATION)
# ================================

def pilih_soal(theta,bank,used):

    best=None
    max_info=-999

    for item in bank:

        if item['id'] in used:
            continue

        if item.get("exposure",0)>=EXPOSURE_LIMIT:
            continue

        info=item_information(theta,item['a'],item['b'],item['c'])

        if info>max_info:

            max_info=info
            best=item

    if best is None:

        best=np.random.choice(bank)

    return best


# ================================
# UPDATE THETA (NEWTON RAPHSON)
# ================================

def update_theta(theta,responses,items):

    numerator=0
    denominator=0

    for i in range(len(responses)):

        item=items[i]

        a=item['a']
        b=item['b']
        c=item['c']

        u=responses[i]

        p=irt_probability(theta,a,b,c)
        q=1-p

        numerator+=a*(u-p)
        denominator+=(a**2)*p*q

    if denominator!=0:

        theta=theta+(numerator/denominator)

    theta=max(THETA_MIN,min(THETA_MAX,theta))

    return theta


# ================================
# STANDARD ERROR
# ================================

def standard_error(theta,items):

    info_sum=0

    for item in items:

        info_sum+=item_information(
            theta,
            item['a'],
            item['b'],
            item['c']
        )

    if info_sum==0:
        return 999

    return 1/math.sqrt(info_sum)


# ================================
# SKOR
# ================================

def transform_ke_100(theta):

    return round(((np.clip(theta,-3,3)+3)/6)*100,2)


# ================================
# LOAD BANK SOAL
# ================================

if "bank_soal" not in st.session_state:

    st.session_state.bank_soal=ambil_bank_soal()


# ================================
# LOAD SESSION
# ================================

saved=load_session()

if saved and "identitas_siap" not in st.session_state:

    st.session_state.update(saved)


# ================================
# INIT STATE
# ================================

if 'identitas_siap' not in st.session_state:
    st.session_state.identitas_siap=False

if 'theta' not in st.session_state:
    st.session_state.theta=0.0

if 'index_soal' not in st.session_state:
    st.session_state.index_soal=0

if 'responses' not in st.session_state:
    st.session_state.responses=[]

if 'soal_selesai' not in st.session_state:
    st.session_state.soal_selesai=[]


# ================================
# LOGIN
# ================================

if not st.session_state.identitas_siap:

    st.title("🛡️ Sistem CAT")

    with st.form("login"):

        nama=st.text_input("Nama")
        nip=st.text_input("Nomor Peserta")

        if st.form_submit_button("Mulai Tes"):

            if nama and nip:

                st.session_state.nama=nama
                st.session_state.nip=nip
                st.session_state.identitas_siap=True

                st.session_state.start_server=time.time()

                save_session({
                    "identitas_siap": st.session_state.identitas_siap,
                    "nama": st.session_state.nama,
                    "nip": st.session_state.nip,
                    "theta": float(st.session_state.theta),
                    "index_soal": int(st.session_state.index_soal),
                    "responses": st.session_state.responses,
                    "soal_selesai": st.session_state.soal_selesai,
                    "start_server": float(st.session_state.start_server)
                })
                st.rerun()


# ================================
# HALAMAN TES
# ================================

else:

    elapsed=time.time()-st.session_state.start_server
    sisa=max(0,SERVER_TIME_LIMIT-int(elapsed))

    st.title("🛡️ CAT Online")

    st.write("Peserta :",st.session_state.nama)

    st.write("Sisa waktu :",sisa,"detik")

    st.progress(st.session_state.index_soal/MAX_ITEMS)

    if sisa<=0:

        st.session_state.index_soal+=1
        st.session_state.start_server=time.time()
        st.rerun()


    se=standard_error(
        st.session_state.theta,
        st.session_state.soal_selesai
    )

    if se<SE_THRESHOLD or st.session_state.index_soal>=MAX_ITEMS:

        skor=transform_ke_100(st.session_state.theta)

        rel=1-(se**2)
        sem=se

        st.success("Tes selesai")

        st.metric("Skor akhir",skor)

        kirim_ke_sheets(
            st.session_state.nama,
            st.session_state.nip,
            st.session_state.theta,
            rel,
            sem,
            skor
        )

        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        st.stop()


    used=[x['id'] for x in st.session_state.soal_selesai]

    soal=pilih_soal(
        st.session_state.theta,
        st.session_state.bank_soal,
        used
    )

    if "exposure" not in soal:
        soal["exposure"]=0

    soal["exposure"]+=0.01


    st.subheader(
        f"Soal {st.session_state.index_soal+1}"
    )

    st.write(soal['teks'])

    opsi=[
        f"A. {soal['opsi_A']}",
        f"B. {soal['opsi_B']}",
        f"C. {soal['opsi_C']}",
        f"D. {soal['opsi_D']}"
    ]

    pilihan=st.radio(
        "Jawaban Anda",
        opsi,
        index=None
    )


    if st.button("Simpan Jawaban"):

        if pilihan:

            skor_biner=1 if pilihan.startswith(soal['kunci']) else 0

            st.session_state.responses.append(skor_biner)

            st.session_state.soal_selesai.append(soal)

            st.session_state.theta=update_theta(
                st.session_state.theta,
                st.session_state.responses,
                st.session_state.soal_selesai
            )

            st.session_state.index_soal+=1

            st.session_state.start_server=time.time()

            save_session(st.session_state)

            st.rerun()

