import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av
import cv2
from typing import List

st.set_page_config(page_title="Ultra QR Scanner", layout="wide")

# ---------------- Session ----------------
if "codes" not in st.session_state:
    st.session_state.codes: List[str] = []
if "dup" not in st.session_state:
    st.session_state.dup = ""

st.title("🚀 Ultra QR Scanner (WeChatDetector)")

# ---------------- WeChat QR Detector ----------------
try:
    wechat_detector = cv2.wechat_qrcode_WeChatQRCode.create()
except Exception:
    wechat_detector = None
    st.warning("WeChat QR detector unavailable (opencv-contrib missing). Falling back to QRCodeDetector.")

basic_detector = cv2.QRCodeDetector()

# ---------------- Video Processor ----------------
class UltraProcessor(VideoProcessorBase):
    def _detect_wechat(self, img):
        if not wechat_detector:
            return []
        res, _ = wechat_detector.detectAndDecode(img)
        return [t for t in res if t]

    def _detect_basic(self, img):
        found = []
        ok, infos, _, _ = basic_detector.detectAndDecodeMulti(img)
        if ok:
            found += [t for t in infos if t]
        else:
            data, _, _ = basic_detector.detectAndDecode(img)
            if data:
                found.append(data)
        return found

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        codes = self._detect_wechat(img)
        if not codes:
            codes = self._detect_basic(img)

        for code in codes:
            if code not in st.session_state.codes:
                st.session_state.codes.append(code)
                st.session_state.dup = ""
            else:
                st.session_state.dup = f"⚠️ Dup: {code}"
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------------- WebRTC ----------------
webrtc_streamer(
    key="ultra",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=UltraProcessor,
    media_stream_constraints={
        "video": {"facingMode": {"ideal": "environment"}, "width": 1920, "height": 1080},
        "audio": False,
    },
)

# ---------------- UI ----------------
if st.session_state.dup:
    st.warning(st.session_state.dup)

st.subheader("Codes")
for idx, c in enumerate(reversed(st.session_state.codes), 1):
    st.write(f"{len(st.session_state.codes)-idx+1}. {c}")
