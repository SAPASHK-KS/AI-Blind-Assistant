# AI Blind Assistant

An AI-powered assistant that describes surroundings aloud for visually impaired users. Captures a scene via camera, analyzes it with **Gemini Vision AI**, and speaks a natural-language description using text-to-speech.

Two modes are included:
- **`app.py`** — Streamlit web app (snapshot-based, browser camera)
- **`main.py`** — Desktop app using OpenCV (live webcam feed, auto mode)

## Features

- Real-time scene description from a camera snapshot
- Audio narration via text-to-speech (gTTS)
- Auto mode (desktop version): describes the scene every 5 seconds
- Simple controls: `SPACE` to describe, `A` for auto mode, `Q` to quit

## Project Structure

```
ai-blind-assistant/
├── app.py              # Streamlit web app
├── main.py             # OpenCV desktop app (live webcam)
└── requirements.txt    # Dependencies
```

## Installation

```bash
git clone https://github.com/<your-username>/AI-Blind-Assistant.git
cd AI-Blind-Assistant/ai-blind-assistant
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install opencv-python pygame   # required only for main.py
```

### API Key

Create a `.env` file in `ai-blind-assistant/`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

## Usage

**Web app:**
```bash
streamlit run app.py
```
Allow camera access, take a snapshot, and click **Describe this Scene**.

**Desktop app:**
```bash
python main.py
```
| Key | Action |
|---|---|
| `SPACE` | Describe the current scene |
| `A` | Toggle auto mode (every 5s) |
| `Q` | Quit |

## How It Works

1. A frame is captured from the camera
2. The image is sent to `gemini-2.5-flash` with a prompt tailored for visually impaired users
3. Gemini returns a concise 2–3 sentence description
4. The description is converted to speech (gTTS) and played back

## Tech Stack

- **Streamlit** — web UI
- **OpenCV + pygame** — desktop UI and audio playback
- **Google Gemini API** (`google-genai`) — scene understanding
- **gTTS** — text-to-speech
- **Pillow** — image handling
