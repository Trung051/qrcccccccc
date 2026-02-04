import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av
import cv2
from typing import List, Tuple

# Optional pyzbar (disabled on cloud)
try:
    from pyzbar.pyzbar import decode as pyzbar_decode  # type: ignore
except Exception:
    pyzbar_decode = None

st.set_page_config(page_title="QR Scanner", layout="wide")

# ---------------- Session State ----------------
if "codes" not in st.session_state:
    st.session_state.codes: List[str] = []
if "duplicate_msg" not in st.session_state:
    st.session_state.duplicate_msg = ""

st.title("🛠️ QR Scanner – siêu nhạy")

st.caption("Camera quét liên tục. Thử giữ QR cách camera 10-20 cm, đủ sáng để nhận nhanh.")

# ---------------- Helper ----------------
def preprocess(img) -> Tuple[cv2.Mat, cv2.Mat]:
    """Return (gray, sharpened) for detection."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    sharpen = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
    return gray, sharpen


# ---------------- Video Processor ----------------
class QRVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def _detect(self, im):
        found = []
        ok, infos, points, _ = self.detector.detectAndDecodeMulti(im)
        if ok:
            found.extend([t for t in infos if t])
            return found, points
        data, pts, _ = self.detector.detectAndDecode(im)
        if data:
            found.append(data)
            points = [pts] if pts is not None else None
            return found, points
        return found, None

    def recv(self, frame: av.VideoFrame):
        img = frame.to_ndarray(format="bgr24")
        gray, sharp = preprocess(img)

        codes, pts = self._detect(sharp)

        # pyzbar fallback if available & nothing found
        if not codes and pyzbar_decode:
            codes = [o.data.decode("utf-8") for o in pyzbar_decode(img)]

        # Draw polygons if detected
        if pts is not None:
            for p in pts:
                if p is not None:
                    p = p.reshape(-1, 2).astype(int)
                    cv2.polylines(img, [p], True, (0, 255, 0), 2)

        for code in codes:
            if code not in st.session_state.codes:
                st.session_state.codes.append(code)
                st.session_state.duplicate_msg = ""
            else:
                st.session_state.duplicate_msg = f"⚠️ Mã trùng: {code}"

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ---------------- WebRTC ----------------
webrtc_streamer(
    key="qr-scanner",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=QRVideoProcessor,
    media_stream_constraints={
        "video": {"facingMode": {"ideal": "environment"}, "width": 1920, "height": 1080},
        "audio": False,
    },
    async_processing=True,
)

# ---------------- UI ----------------
if st.session_state.duplicate_msg:
    st.warning(st.session_state.duplicate_msg)

st.subheader("Danh sách mã đã quét")
with st.container():
    for idx, code in enumerate(reversed(st.session_state.codes), 1):
        st.write(f"{len(st.session_state.codes) - idx + 1}. {code}")

left, right = st.columns(2)
with left:
    if st.button("🔄 Làm mới danh sách"):
        st.session_state.codes.clear()
        st.session_state.duplicate_msg = ""
with right:
    st.write(f"Tổng: {len(st.session_state.codes)} mã")
