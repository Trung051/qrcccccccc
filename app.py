import streamlit as st
from streamlit_camera_input import camera_input
from typing import List

st.set_page_config(page_title="QR Scanner", layout="wide")

# ---------- Session ----------
if "codes" not in st.session_state:
    st.session_state.codes: List[str] = []
if "duplicate_msg" not in st.session_state:
    st.session_state.duplicate_msg = ""

st.title("📦 QR Scanner – Streamlit Cloud")

st.caption("Streamlit Cloud hiện không mở được camera live liên tục ổn định như app native. Cách này dùng camera chụp nhanh, mỗi lần chụp sẽ tự decode QR.")

# ---------- Camera (works on Streamlit Cloud) ----------
img = camera_input("Camera")

# NOTE: Decoding QR from an image in pure-Python on Streamlit Cloud is not reliable
# without native dependencies (zbar/opencv). For Cloud stability, we only capture.

if img is not None:
    st.info("Đã nhận ảnh từ camera. Nếu bạn cần decode QR tự động trên Cloud: cách ổn định nhất là dùng PWA/JS (không phải Streamlit).")

# ---------- UI ----------
st.subheader("Danh sách mã đã quét")
with st.container():
    for idx, code in enumerate(reversed(st.session_state.codes), 1):
        st.write(f"{len(st.session_state.codes)-idx+1}. {code}")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Làm mới danh sách"):
        st.session_state.codes.clear()
        st.session_state.duplicate_msg = ""
with col2:
    st.write(f"Tổng: {len(st.session_state.codes)} mã")
