import streamlit as st
import numpy as np
import requests
import time
import json
import math
import os

st.set_page_config(page_title="CAT Online", layout="wide")

SESSION_FILE="cat_session.json"

THETA_MIN=-4
THETA_MAX=4

MAX_ITEMS=30
SE_THRESHOLD=0.30
EXPOSURE_LIMIT=0.25

TIME_LIMIT=60


# =============================
# SESSION SAVE / LOAD
# =============================

def save_session():

    data={
        "identitas_siap":st.session_state.identitas_siap,
        "nama":st.session_state.get("nama",""),
        "nip":st.session_state.get("nip",""),
        "theta":float(st.session_state.theta),
        "index_soal":int(st.session_state.index_soal),
        "responses":st.session_state.responses,
        "items":st.session_state.items,
        "start_server":float(st.session_state.start_server)
    }

    with open(SESSION_FILE,"w") as f:
        json.dump(data,f)


def load_session():

    if os.path.exists(SESSION_FILE):

        with open(SESSION_FILE,"r") as f:
            return json.load(f)

    return None


# =============================
# LOAD BANK SOAL
# =============================

@st.cache_data(ttl=60)
def ambil_bank_soal():

    url="https://script.google.com/macros/s/AKfycbzJXP_5EZMX56yP38-qxW919cJPGOC0KnX_HEtyXyKKMILViO0OTdwtpGH81MBZ7042Ng/exec"

    try:
        r=requests.get(url)
        data=r.json()

        for i in data:

            i["a"]=float(i["a"])
            i["b"]=float(i["b"])
            i["c"]=float(i["c"])

        return data

    except:
        return []


# =============================
# IRT 3PL
# =============================

def irt_probability(theta,a,b,c):

    return c+(1-c)/(1+math.exp(-a*(theta-b)))


def item_information(theta,a,b,c):

    p=irt_probability(theta,a,b,c)

    q=1-p

    if p<=0 or q<=0:
        return 0

    info=(a*a*(p-c)*(p-c))/((1-c)*(1-c)*p*q)

    return info


# =============================
# SELECT ITEM
# =============================

def pilih_soal(theta,bank,used):

    best=None
    max_info=-1

    for item in bank:

        if item["id"] in used:
            continue

        if item.get("exposure",0)>=EXPOSURE_LIMIT:
            continue

        info=item_information(theta,item["a"],item["b"],item["c"])

        if info>max_info:

            max_info=info
            best=item

    if best is None:

        sisa=[x for x in bank if x["id"] not in used]

        if len(sisa)>0:
            best=np.random.choice(sisa)
        else:
            best=np.random.choice(bank)

    return best


# =============================
# UPDATE THETA
# =============================

def update_theta(theta,responses,items):

    num=0
    den=0

    for i in range(len(responses)):

        item=items[i]

        a=item["a"]
        b=item["b"]
        c=item["c"]

        u=responses[i]

        p=irt_probability(theta,a,b,c)

        q=1-p

        num+=a*(u-p)
        den+=a*a*p*q

    if den!=0:

        theta=theta+(num/den)

    theta=max(THETA_MIN,min(THETA_MAX,theta))

    return theta


# =============================
# STANDARD ERROR
# =============================

def standard_error(theta,items):

    info_sum=0

    for item in items:

        info_sum+=item_information(
            theta,
            item["a"],
            item["b"],
            item["c"]
        )

    if info_sum==0:
        return 999

    return 1/math.sqrt(info_sum)


# =============================
# SKOR
# =============================

def score(theta):

    return round(((np.clip(theta,-3,3)+3)/6)*100,2)


# =============================
# INIT SESSION
# =============================

saved=load_session()

if saved and "identitas_siap" not in st.session_state:

    for k,v in saved.items():
        st.session_state[k]=v


if "identitas_siap" not in st.session_state:
    st.session_state.identitas_siap=False

if "theta" not in st.session_state:
    st.session_state.theta=0.0

if "index_soal" not in st.session_state:
    st.session_state.index_soal=0

if "responses" not in st.session_state:
    st.session_state.responses=[]

if "items" not in st.session_state:
    st.session_state.items=[]


# =============================
# LOAD BANK
# =============================

bank=ambil_bank_soal()


# =============================
# LOGIN
# =============================

if not st.session_state.identitas_siap:

    st.title("🛡️ Sistem CAT")

    with st.form("login"):

        nama=st.text_input("Nama")
        nip=st.text_input("Nomor Peserta")

        if st.form_submit_button("Mulai Tes"):

            if nama and nip and len(bank)>0:

                st.session_state.nama=nama
                st.session_state.nip=nip
                st.session_state.identitas_siap=True

                st.session_state.start_server=time.time()

                save_session()

                st.rerun()


# =============================
# HALAMAN TES
# =============================

else:

    elapsed=time.time()-st.session_state.start_server

    sisa=max(0,TIME_LIMIT-int(elapsed))

    st.title("CAT Online")

    st.write("Peserta :",st.session_state.nama)

    st.write("Sisa waktu :",sisa)

    st.progress(st.session_state.index_soal/MAX_ITEMS)

    if sisa<=0:

        st.session_state.index_soal+=1
        st.session_state.start_server=time.time()

        save_session()

        st.rerun()


    se=standard_error(
        st.session_state.theta,
        st.session_state.items
    )

    if se<SE_THRESHOLD or st.session_state.index_soal>=MAX_ITEMS:

        skor=score(st.session_state.theta)

        rel=1-(se*se)

        st.success("Tes selesai")

        st.metric("Skor akhir",skor)

        st.write("Reliabilitas :",round(rel,3))

        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        st.stop()


    used=[x["id"] for x in st.session_state.items]

    soal=pilih_soal(
        st.session_state.theta,
        bank,
        used
    )

    st.subheader("Soal "+str(st.session_state.index_soal+1))

    st.write(soal["teks"])

    opsi=[
        "A. "+soal["opsi_A"],
        "B. "+soal["opsi_B"],
        "C. "+soal["opsi_C"],
        "D. "+soal["opsi_D"]
    ]

    pilih=st.radio("Jawaban",opsi,index=None)

    if st.button("Simpan Jawaban"):

        if pilih:

            skor_biner=1 if pilih.startswith(soal["kunci"]) else 0

            st.session_state.responses.append(skor_biner)

            st.session_state.items.append(soal)

            st.session_state.theta=update_theta(
                st.session_state.theta,
                st.session_state.responses,
                st.session_state.items
            )

            st.session_state.index_soal+=1

            st.session_state.start_server=time.time()

            save_session()

            st.rerun()
