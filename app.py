import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av
import cv2

st.set_page_config(page_title="QR Scanner", layout="wide")

# Initialize session state
if "codes" not in st.session_state:
    st.session_state.codes = []  # list to preserve order
if "duplicate_msg" not in st.session_state:
    st.session_state.duplicate_msg = ""

st.title("📦 Quét mã QR liên tục")

st.caption("Camera sẽ liên tục quét. Mã mới sẽ hiển thị dưới khung camera. Nếu mã đã quét, sẽ báo trùng.")

class QRVideoProcessor(VideoProcessorBase):
    """Continuously process video frames to detect QR codes (opencv only)."""

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def recv(self, frame: av.VideoFrame):
        img = frame.to_ndarray(format="bgr24")

        found_codes = []
        data, bbox, _ = self.detector.detectAndDecode(img)
        if data:
            found_codes.append(data)

        for code in found_codes:
            if code not in st.session_state.codes:
                st.session_state.codes.append(code)
                st.session_state.duplicate_msg = ""
            else:
                st.session_state.duplicate_msg = f"⚠️ Mã trùng: {code}"

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Start WebRTC streamer
webrtc_ctx = webrtc_streamer(
    key="qr-scanner",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=QRVideoProcessor,
    media_stream_constraints={
        "video": {
            "facingMode": {"ideal": "environment"}  # use back camera on mobile
        },
        "audio": False,
    },
    async_processing=True,
)

# Display duplicate message if any
if st.session_state.duplicate_msg:
    st.warning(st.session_state.duplicate_msg)

st.subheader("Danh sách mã đã quét")

# Show as a scrollable container
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
