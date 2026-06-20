import cv2
import os
import tempfile
import threading
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image
from gtts import gTTS
import pygame

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
pygame.mixer.init()

# ── State ──────────────────────────────────────────
is_processing = False
auto_mode     = False
last_auto     = 0
AUTO_INTERVAL = 5
current_desc  = ""

# ── Helpers ────────────────────────────────────────
def speak(text):
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp = f.name
        tts.save(tmp)
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        os.unlink(tmp)
    except Exception as e:
        print(f"⚠️  Speech error: {e}")

def describe_scene(frame):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        tmp = f.name
    cv2.imwrite(tmp, frame)
    img = Image.open(tmp)
    prompt = """You are an assistant helping a visually impaired person understand their surroundings.
Describe what you see in 2-3 clear, natural sentences.
Mention objects, people, distances if guessable, and anything important.
Be concise, calm and helpful. Start directly with the description."""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, img]
    )
    os.unlink(tmp)
    return resp.text.strip()

def analyze_and_speak(frame):
    global is_processing, current_desc
    try:
        desc = describe_scene(frame)
        current_desc = desc
        print(f"\n🗣️  {desc}\n" + "─" * 55)
        speak(desc)
    except Exception as e:
        current_desc = "Could not analyze scene."
        print(f"❌ Error: {e}")
        speak("Sorry, I could not analyze the scene.")
    finally:
        is_processing = False

def trigger(frame):
    global is_processing
    if is_processing:
        return
    is_processing = True
    t = threading.Thread(target=analyze_and_speak, args=(frame.copy(),))
    t.daemon = True
    t.start()

def draw_overlay(frame, desc, auto, processing):
    h, w = frame.shape[:2]

    # ── top status bar ──
    if processing:
        bar_color   = (0, 165, 255)
        status_text = "Analyzing... please wait"
    elif auto:
        bar_color   = (0, 180, 60)
        status_text = "AUTO ON (every 5s)  |  A: Stop Auto  |  Q: Quit"
    else:
        bar_color   = (50, 50, 50)
        status_text = "SPACE: Describe  |  A: Auto Mode  |  Q: Quit"

    cv2.rectangle(frame, (0, 0), (w, 44), bar_color, -1)
    cv2.putText(frame, status_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # ── auto mode countdown bar ──
    if auto and not processing:
        elapsed  = time.time() - last_auto
        progress = min(elapsed / AUTO_INTERVAL, 1.0)
        cv2.rectangle(frame, (0, 44), (int(w * progress), 50), (0, 220, 80), -1)
        cv2.rectangle(frame, (0, 44), (w, 50), (80, 80, 80), 1)

    # ── description box at bottom ──
    if desc:
        words      = desc.split()
        lines, cur = [], ""
        for word in words:
            test = (cur + " " + word).strip()
            if cv2.getTextSize(test, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0][0] < w - 20:
                cur = test
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)

        line_h = 24
        box_h  = len(lines) * line_h + 20
        cv2.rectangle(frame, (0, h - box_h - 5), (w, h), (20, 20, 20), -1)
        for i, line in enumerate(lines):
            cv2.putText(frame, line,
                        (10, h - box_h + 10 + i * line_h),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)
    return frame

# ── Main loop ──────────────────────────────────────
cap = cv2.VideoCapture(0)
print("✅  AI Blind Assistant started!")
print("📌  SPACE → describe once | A → auto mode (every 5s) | Q → quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()

    # ── Auto mode: fire every AUTO_INTERVAL seconds ──
    if auto_mode and not is_processing:
        if (now - last_auto) >= AUTO_INTERVAL:
            last_auto = now
            print("🔄  Auto: Analyzing scene...")
            trigger(frame)

    # ── Draw UI ──
    display = draw_overlay(frame.copy(), current_desc, auto_mode, is_processing)
    cv2.imshow("AI Blind Assistant", display)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("👋Seeeyaaaa!!!")
        break

    elif key == ord(' '):
        if not auto_mode:
            print("🔍  Analyzing scene...")
            trigger(frame)
        else:
            print("⚠️  Turn off auto mode first (press A)")

    elif key == ord('a'):
        auto_mode = not auto_mode
        last_auto = time.time()  # reset timer on toggle
        if auto_mode:
            print("🟢  Auto mode ON — describing every 5 seconds!")
            speak("Auto mode on. I will describe the scene every 5 seconds.")
        else:
            print("🔴  Auto mode OFF")
            speak("Auto mode off.")

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()