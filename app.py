import streamlit as st
from streamlit_javascript import st_javascript
from typing import List

st.set_page_config(page_title="QR Scanner", layout="wide")

# ---------- Session ----------
if "codes" not in st.session_state:
    st.session_state.codes: List[str] = []
if "duplicate_msg" not in st.session_state:
    st.session_state.duplicate_msg = ""

st.title("📦 QR Scanner – Mobile First (Cloud Ready)")

st.caption("Quét liên tục bằng camera điện thoại. Đưa QR vào là tự nhận.")

# ---------- JS/HTML ----------
html = """
<div id="reader" style="width:100%;height:55vh;min-height:300px;background:#111827;border-radius:12px;"></div>
<script src="https://unpkg.com/html5-qrcode@2.3.10/html5-qrcode.min.js"></script>
<script>
const html5QrCode = new Html5Qrcode("reader");
let last = "";
let lastAt = 0;
const DEDUPE = 1200;

function onScanSuccess(text, result) {
  const now = Date.now();
  if (text === last && (now - lastAt) < DEDUPE) return;
  last = text; lastAt = now;
  window.parent.postMessage({type:"qr", text:text, ts:now}, "*");
}

function onScanFailure(err) {}

(async()=>{
  const cams = await Html5Qrcode.getCameras();
  const back = cams?.find(c=>c.label?.toLowerCase().includes('back') || c.label?.toLowerCase().includes('environment'));
  const camId = (back || cams?.[0])?.id;
  if (!camId) { console.error('No camera'); return; }
  await html5QrCode.start(
    { deviceId: { exact: camId } },
    { fps:24, qrbox:{width:250,height:250} },
    onScanSuccess,
    onScanFailure
  );
})();
</script>
"""
st.components.v1.html(html, height=400)

# ---------- Receive QR from JS ----------
qr_result = st_javascript("""
window.addEventListener('message', (e)=>{
  if(e.data.type==='qr') {
    window.qrResult = e.data;
  }
});
""")

if qr_result and "text" in qr_result:
    txt = qr_result["text"]
    if txt not in st.session_state.codes:
        st.session_state.codes.append(txt)
        st.session_state.duplicate_msg = ""
    else:
        st.session_state.duplicate_msg = f"⚠️ Mã trùng: {txt}"

# ---------- UI ----------
if st.session_state.duplicate_msg:
    st.warning(st.session_state.duplicate_msg)

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
