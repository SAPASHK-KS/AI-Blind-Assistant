import streamlit as st
import os
import tempfile
from google import genai
from PIL import Image
from gtts import gTTS
from dotenv import load_dotenv

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
    .main { background-color: #0f0f0f; }
    .block-container { padding-top: 2rem; }

    .title-box {
        text-align: center;
        padding: 2rem 1rem 1rem;
    }
    .title-box h1 {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .title-box p {
        font-size: 1.05rem;
        color: #aaaaaa;
        margin-top: 0;
    }

    .desc-box {
        background: #1a1a2e;
        border-left: 4px solid #00c896;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-top: 1.2rem;
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
        transition: opacity 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.85;
    }

    .how-box {
        background: #111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 2rem;
        color: #aaa;
        font-size: 0.9rem;
    }
    .how-box h4 {
        color: #fff;
        margin-bottom: 0.5rem;
    }

    .footer {
        text-align: center;
        color: #444;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-bottom: 2rem;
    }
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

def text_to_audio(text: str) -> str:
    tts = gTTS(text=text, lang="en", slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        path = f.name
    tts.save(path)
    return path

# ── UI ────────────────────────────────────────────
st.markdown("""
<div class="title-box">
    <h1>🤖 AI Blind Assistant</h1>
    <p>Eyes for the visually impaired — powered by Gemini Vision AI</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Camera input
st.markdown("### 📷 Capture a Scene")
camera_image = st.camera_input(
    label="Point your camera and take a snapshot",
    label_visibility="collapsed"
)

if camera_image:
    img = Image.open(camera_image).convert("RGB")
    st.image(img, caption="Captured Scene", use_column_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Describe this Scene"):
        with st.spinner("🧠 Gemini is analyzing the scene..."):
            try:
                description = describe_image(img)

                # Description box
                st.markdown(f"""
                <div class="desc-box">
                    <div class="badge">🗣️ AI Description</div><br>
                    {description}
                </div>
                """, unsafe_allow_html=True)

                # Audio
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🔊 Listen")
                audio_path = text_to_audio(description)
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                os.unlink(audio_path)

            except Exception as e:
                st.error(f"❌ Error: {e}")

else:
    # How it works section
    st.markdown("""
    <div class="how-box">
        <h4>⚡ How it works</h4>
        <ol>
            <li>Allow camera access when prompted</li>
            <li>Point your camera at any scene or environment</li>
            <li>Click <b>Describe this Scene</b></li>
            <li>Gemini Vision AI analyzes the image</li>
            <li>A natural language description is spoken aloud</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="how-box" style="margin-top:1rem;">
        <h4>🛠️ Tech Stack</h4>
        <p>
        🧠 <b>Google Gemini 2.5 Flash</b> — Vision AI<br>
        👁️ <b>OpenCV + PIL</b> — Image processing<br>
        🔊 <b>gTTS</b> — Text to Speech<br>
        🌐 <b>Streamlit</b> — Web interface
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Built with ❤️ using Gemini Vision AI + Streamlit &nbsp;|&nbsp; Data Science Portfolio Project
</div>
""", unsafe_allow_html=True)