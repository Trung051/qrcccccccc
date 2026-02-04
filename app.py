import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av
import cv2
from typing import List

# Try import pyzbar for better barcode support (optional)
pyzbar_decode = None  # disabled on Streamlit Cloud (no zbar)

st.set_page_config(page_title="QR Scanner", layout="wide")

# ---------- Session State ----------
if "codes" not in st.session_state:
    st.session_state.codes: List[str] = []  # preserve order
if "duplicate_msg" not in st.session_state:
    st.session_state.duplicate_msg = ""

st.title("📦 Quét mã QR / Barcode liên tục")

st.caption(
    "Camera sẽ liên tục quét. Mã mới hiển thị dưới khung camera. Nếu mã đã quét, sẽ báo trùng."  # noqa: E501
)

# ---------- Video Processor ----------
class QRVideoProcessor(VideoProcessorBase):
    """Detect QR & barcodes continuously, no blocking."""

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def _detect_opencv(self, img):
        # Try multi-QR first
        found = []
        retval, decoded_info, _, _ = self.detector.detectAndDecodeMulti(img)
        if retval:
            found.extend([txt for txt in decoded_info if txt])
        else:
            # Fallback single
            data, _, _ = self.detector.detectAndDecode(img)
            if data:
                found.append(data)
        return found

    def _detect_pyzbar(self, img):
        if not pyzbar_decode:
            return []
        return [obj.data.decode("utf-8") for obj in pyzbar_decode(img)]

    def recv(self, frame: av.VideoFrame):
        img = frame.to_ndarray(format="bgr24")

        found_codes = self._detect_opencv(img)
        

        for code in found_codes:
            if code not in st.session_state.codes:
                st.session_state.codes.append(code)
                st.session_state.duplicate_msg = ""
            else:
                st.session_state.duplicate_msg = f"⚠️ Mã trùng: {code}"

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------- WebRTC Stream ----------
webrtc_streamer(
    key="qr-scanner",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=QRVideoProcessor,
    media_stream_constraints={
        "video": {
            "facingMode": {"ideal": "environment"},
            "width": 1280,
            "height": 720,
        },
        "audio": False,
    },
    async_processing=True,
)

# ---------- UI ----------
if st.session_state.duplicate_msg:
    st.warning(st.session_state.duplicate_msg)

st.subheader("Danh sách mã đã quét")

with st.container():
    # show newest first
    for idx, code in enumerate(reversed(st.session_state.codes), 1):
        st.write(f"{len(st.session_state.codes) - idx + 1}. {code}")

left, right = st.columns(2)
with left:
    if st.button("🔄 Làm mới danh sách"):
        st.session_state.codes.clear()
        st.session_state.duplicate_msg = ""
with right:
    st.write(f"Tổng: {len(st.session_state.codes)} mã")
