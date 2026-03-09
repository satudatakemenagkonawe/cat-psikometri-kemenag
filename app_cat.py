import streamlit as st
import time
import json

from irt import update_theta_mle
from selection import select_next_item
from config import MAX_ITEM, TARGET_SE, TEST_TIME

# =========================
# SESSION INIT
# =========================

defaults = {
    "theta": 0.0,
    "se": 10,
    "administered_items": [],
    "responses": {},
    "start_time": None,
    "pid": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =========================
# LOGIN PESERTA
# =========================

if st.session_state.pid is None:

    pid = st.text_input("ID Peserta")

    if st.button("Mulai Tes"):

        st.session_state.pid = pid
        st.session_state.start_time = time.time()

        st.rerun()

    st.stop()


# =========================
# TIMER SERVER
# =========================

elapsed = time.time() - st.session_state.start_time
remaining = TEST_TIME - elapsed

if remaining <= 0:

    st.error("Waktu habis")
    st.stop()

st.sidebar.write("Sisa waktu:", int(remaining), "detik")


# =========================
# BANK SOAL
# =========================

bank = [
    {"id": 1, "a": 1.1, "b": -0.5, "c": 0.2, "q": "Soal 1"},
    {"id": 2, "a": 1.2, "b": 0.0, "c": 0.2, "q": "Soal 2"},
    {"id": 3, "a": 0.9, "b": 0.7, "c": 0.2, "q": "Soal 3"},
]


used_ids = [x["id"] for x in st.session_state.administered_items]


# =========================
# PILIH ITEM BERIKUTNYA
# =========================

item = select_next_item(
    st.session_state.theta,
    bank,
    used_ids,
    {},
)

if item is None:

    st.success("Tes selesai")
    st.stop()


# =========================
# TAMPILKAN SOAL
# =========================

st.write(item["q"])

ans = st.radio(
    "Jawaban",
    ["A", "B", "C", "D"],
    key=f"ans_{item['id']}",
)


if st.button("Next"):

    score = 1 if ans == "A" else 0

    st.session_state.responses[item["id"]] = score
    st.session_state.administered_items.append(item)

    st.session_state.theta = update_theta_mle(
        st.session_state.theta,
        st.session_state.administered_items,
        st.session_state.responses,
    )

    st.rerun()


# =========================
# STOP RULE
# =========================

if len(st.session_state.administered_items) >= MAX_ITEM:

    st.success("Tes selesai")
    st.stop()
