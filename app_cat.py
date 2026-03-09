import streamlit as st
import requests
import numpy as np
import math
import time
import uuid

st.set_page_config(page_title="CAT Online",layout="wide")

API_URL="https://script.google.com/macros/s/AKfycbwtdEei5DFD95dlEvegxqS1oorA7Nr1H44k2s6SqysuvomcSH119cbV04gvt40h5A_qrA/exec"

MAX_THETA=30
SE_THRESHOLD=0.30
TIME_LIMIT=60

# ======================================
# SESSION INITIALIZER (WAJIB UNTUK CAT)
# ======================================

def init_session():

    defaults = {
        "theta": 0,
        "se": 999,
        "item": [],
        "answers": {},
        "start_time": None,
        "finished": False
    }

    for k,v in defaults.item():
        if k not in st.session_state:
            st.session_state[k] = v
    init_session()
    if "item_history" not in st.session_state:
        st.session_state.item_history = []

# =====================
# LOAD BANK SOAL
# =====================

@st.cache_data(ttl=60)
def load_bank():

    r=requests.get(API_URL)

    data=r.json()

    for i in data:

        i["a"]=float(i["a"])
        i["b"]=float(i["b"])
        i["c"]=float(i["c"])

    return data


# =====================
# IRT FUNCTIONS
# =====================

def prob(theta,a,b,c):

    return c+(1-c)/(1+math.exp(-a*(theta-b)))


def information(theta,a,b,c):

    p=prob(theta,a,b,c)

    q=1-p

    if p<=0 or q<=0:
        return 0

    return (a*a*(p-c)*(p-c))/((1-c)*(1-c)*p*q)


# =====================
# SELECT ITEM
# =====================

def select_item(theta,bank,used):

    best=None
    max_info=-1

    for item in bank:

        if item["id"] in used:
            continue

        info=information(theta,item["a"],item["b"],item["c"])

        if info>max_info:

            max_info=info
            best=item

    return best


# =====================
# UPDATE THETA
# =====================

def update_theta(theta,responses,item):

    num=0
    den=0

    for i in range(len(responses)):

        item=item[i]

        a=item["a"]
        b=item["b"]
        c=item["c"]

        u=responses[i]

        p=prob(theta,a,b,c)

        q=1-p

        num+=a*(u-p)
        den+=a*a*p*q

    if den!=0:

        theta=theta+(num/den)

    return theta


# =====================
# STANDARD ERROR
# =====================

def se(theta,item):

    info=0

    for item in item:

        info+=information(theta,item["a"],item["b"],item["c"])

    if info==0:
        return 999

    return 1/math.sqrt(info)


# =====================
# SCORE
# =====================

def score(theta):

    return round(((np.clip(theta,-3,3)+3)/6)*100,2)


# =====================
# INIT
# =====================

bank=load_bank()

if "session_id" not in st.session_state:

    st.session_state.session_id=str(uuid.uuid4())

    st.session_state.theta=0

    st.session_state.index=0

    st.session_state.responses=[]

    st.session_state.item_history=[]

    st.session_state.start=time.time()


# =====================
# LOGIN
# =====================

if "nama" not in st.session_state:

    st.title("Login CAT")

    nama=st.text_input("Nama")

    nip=st.text_input("Nomor Peserta")

    if st.button("Mulai Tes"):

        st.session_state.nama=nama
        st.session_state.nip=nip

        st.rerun()


# =====================
# TES
# =====================

else:

    elapsed=time.time()-st.session_state.start

    sisa=max(0,TIME_LIMIT-int(elapsed))

    st.title("CAT Online")

    st.write("Peserta:",st.session_state.nama)

    st.write("Waktu:",sisa)

    if sisa<=0:

        st.session_state.index+=1
        st.session_state.start=time.time()

        st.rerun()


    if st.session_state.index>=MAX_ITEM:

        final=score(st.session_state.theta)

        st.success("Tes selesai")

        st.metric("Skor",final)

        st.stop()


    # memastikan session selalu valid
    if "item" not in st.session_state or not isinstance(st.session_state.item_history, list):
        st.session_state.item_history = []

    used = [x["id"] for x in st.session_state.item_history if isinstance(x, dict) and "id" in x]
    soal=select_item(
        st.session_state.theta,
        bank,
        used
    )
    st.write(type(st.session_state.item_history))
    st.subheader("Soal "+str(st.session_state.index+1))

    st.write(soal["teks"])

    opsi=[
        "A. "+soal["opsi_A"],
        "B. "+soal["opsi_B"],
        "C. "+soal["opsi_C"],
        "D. "+soal["opsi_D"]
    ]

    pilih=st.radio("Jawaban",opsi,index=None)

    if st.button("Simpan"):

        skor=1 if pilih.startswith(soal["kunci"]) else 0

        st.session_state.responses.append(skor)

        st.session_state.item_history.append(soal)

        st.session_state.theta=update_theta(
            st.session_state.theta,
            st.session_state.responses,
            st.session_state.item_history
        )

        st.session_state.index+=1

        st.session_state.start=time.time()

        st.rerun()




