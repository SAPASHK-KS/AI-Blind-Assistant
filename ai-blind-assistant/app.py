import streamlit as st
import os
import tempfile
import time
from google import genai
from PIL import Image
from gtts import gTTS
from dotenv import load_dotenv
import base64

load_dotenv()

# ── Page config ───────────────────────────────────
st.set_page_config(
    page_title="AI Blind Assistant",
    page_icon="🤖",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }

    .title-box {
        text-align: center;
        padding: 1.5rem 1rem 0.5rem;
    }
    .title-box h1 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .title-box p {
        font-size: 1rem;
        color: #aaaaaa;
        margin-top: 0;
    }
    .desc-box {
        background: #1a1a2e;
        border-left: 4px solid #00c896;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        color: #e0e0e0;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .badge {
        display: inline-block;
        background: #00c896;
        color: #000;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00c896, #0077ff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
    }
    .auto-badge {
        background: #ff4444;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.5rem;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%   { opacity: 1; }
        50%  { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .footer {
        text-align: center;
        color: #444;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-bottom: 2rem;
    }
    .how-box {
        background: #111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        color: #aaa;
        font-size: 0.9rem;
    }
    .how-box h4 { color: #fff; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Gemini client ─────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)

client = get_client()

# ── Core functions ────────────────────────────────
def describe_image(pil_image: Image.Image) -> str:
    prompt = """You are an assistant helping a visually impaired person understand their surroundings.
Describe what you see in 2-3 clear, natural sentences.
Mention objects, people, distances if guessable, and anything important.
Be concise, calm and helpful. Start directly with the description."""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, pil_image]
    )
    return resp.text.strip()

def text_to_audio_b64(text: str) -> str:
    """Convert text to base64 MP3 for autoplay."""
    tts = gTTS(text=text, lang="en", slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        path = f.name
    tts.save(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    os.unlink(path)
    return b64

def autoplay_audio(b64_audio: str):
    """Inject an autoplay audio tag into the page."""
    st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

def analyze_and_play(image):
    """Describe image and autoplay the audio."""
    with st.spinner("🧠 Analyzing scene..."):
        description = describe_image(image)

    st.markdown(f"""
    <div class="desc-box">
        <div class="badge">🗣️ AI Description</div><br>
        {description}
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("🔊 Generating voice..."):
        b64 = text_to_audio_b64(description)
    autoplay_audio(b64)
    return description

# ── Session state ─────────────────────────────────
if "auto_mode" not in st.session_state:
    st.session_state.auto_mode = False
if "last_capture_time" not in st.session_state:
    st.session_state.last_capture_time = 0

# ── UI ────────────────────────────────────────────
st.markdown("""
<div class="title-box">
    <h1>🤖 AI Blind Assistant</h1>
    <p>Eyes for the visually impaired — powered by Gemini Vision AI</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Mode toggle ───────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("📸 Manual Mode" if st.session_state.auto_mode else "✅ Manual Mode (Active)"):
        st.session_state.auto_mode = False
        st.rerun()
with col2:
    if st.button("🔄 Auto Mode (Active)" if st.session_state.auto_mode else "🔄 Auto Mode (every 5s)"):
        st.session_state.auto_mode = True
        st.session_state.last_capture_time = 0
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── MANUAL MODE ───────────────────────────────────
if not st.session_state.auto_mode:
    st.markdown("### 📷 Take a Photo")
    camera_image = st.camera_input(
        label="camera",
        label_visibility="collapsed",
        key="manual_cam"
    )

    if camera_image:
        img = Image.open(camera_image).convert("RGB")
        # Auto analyze immediately after photo is taken
        analyze_and_play(img)

    else:
        st.markdown("""
        <div class="how-box">
            <h4>📌 How to use — Manual Mode</h4>
            <ol>
                <li>Allow camera access when prompted</li>
                <li>Click <b>Take Photo</b> to capture the scene</li>
                <li>Gemini instantly analyzes and describes it</li>
                <li>Audio plays automatically — no button needed!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# ── AUTO MODE ─────────────────────────────────────
else:
    st.markdown('<div class="auto-badge">🔴 AUTO MODE ON — Capturing every 5 seconds</div>', unsafe_allow_html=True)
    st.markdown("### 📷 Live Camera")

    camera_image = st.camera_input(
        label="camera",
        label_visibility="collapsed",
        key="auto_cam"
    )

    if camera_image:
        now = time.time()
        if (now - st.session_state.last_capture_time) >= 5:
            st.session_state.last_capture_time = now
            img = Image.open(camera_image).convert("RGB")
            analyze_and_play(img)
            # Wait 5 seconds then rerun to capture again
            time.sleep(5)
            st.rerun()
        else:
            remaining = int(5 - (now - st.session_state.last_capture_time))
            st.info(f"⏳ Next capture in {remaining} seconds...")
            time.sleep(1)
            st.rerun()
    else:
        st.markdown("""
        <div class="how-box">
            <h4>📌 How to use — Auto Mode</h4>
            <ol>
                <li>Allow camera access</li>
                <li>Take the first photo to start</li>
                <li>The app will automatically capture and describe every 5 seconds</li>
                <li>Audio plays automatically each time!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with ❤️ using Gemini Vision AI + Streamlit &nbsp;|&nbsp; Data Science Portfolio Project
</div>
""", unsafe_allow_html=True)