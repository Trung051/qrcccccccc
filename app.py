import streamlit as st
from typing import List
import qr_scanner_component as qrc

st.set_page_config(page_title="QR Scanner", layout="wide")

# ---------- Session ----------
if "codes" not in st.session_state:
    st.session_state.codes: List[str] = []
if "duplicate_msg" not in st.session_state:
    st.session_state.duplicate_msg = ""

st.title("📦 QR Scanner – Mobile First (Cloud Ready)")

st.caption("Quét liên tục bằng camera điện thoại. Không cần nút, đưa QR vào là tự nhận.")

# ---------- Component ----------
result = qrc.qr_scanner(key="reader")
if result:
    text = result.get("text")
    if text:
        if text not in st.session_state.codes:
            st.session_state.codes.append(text)
            st.session_state.duplicate_msg = ""
        else:
            st.session_state.duplicate_msg = f"⚠️ Mã trùng: {text}"

# ---------- UI ----------
if st.session_state.duplicate_msg:
    st.warning(st.session_state.duplicate_msg)

st.subheader("Danh sách mã đã quét")

with st.container():
    for idx, code in enumerate(reversed(st.session_state.codes), 1):
        st.write(f"{len(st.session_state.codes) - idx + 1}. {code}")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Làm mới danh sách"):
        st.session_state.codes.clear()
        st.session_state.duplicate_msg = ""
with col2:
    st.write(f"Tổng: {len(st.session_state.codes)} mã")