import streamlit as st
from audio_recorder_streamlit import audio_recorder
from faster_whisper import WhisperModel
import json
import os
from datetime import datetime

DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Still", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600&family=Inter:wght@400;500&display=swap');

header[data-testid="stHeader"] { display: none; }
div[data-testid="stToolbar"] { display: none; }

.stApp {
    background: linear-gradient(135deg, #fdf6ec 0%, #fde4ea 25%, #eaeaf7 55%, #e3edf7 80%);
    font-family: 'Inter', sans-serif;
}
h1, h2, h3, h4 { font-family: 'Lora', serif !important; color: #2b2b2b !important; }
p, span, label { color: #5a5a5a; }

[data-testid="stSidebar"] { background-color: #f7f4ee; border-right: 1px solid #e6e2d6; }
[data-testid="stSidebar"] h3 { color: #2b2b2b !important; }

div.stButton > button {
    border-radius: 999px;
    border: none;
    padding: 0.5rem 1.3rem;
    font-weight: 500;
    width: 100%;
}
button[data-testid="stBaseButton-primary"] { background-color: #4d8b7f !important; color: white !important; }
button[data-testid="stBaseButton-primary"]:hover { background-color: #3d7266 !important; }
button[data-testid="stBaseButton-secondary"] { background-color: transparent !important; color: #4a4a4a !important; border: 1px solid #d8d3c5 !important; }
button[data-testid="stBaseButton-secondary"]:hover { background-color: #ece8de !important; }

div.stDownloadButton > button {
    border-radius: 999px; background-color: white; color: #4d8b7f; border: 1px solid #4d8b7f;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(255,255,255,0.8);
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.6) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.05);
}

iframe { border-radius: 999px; max-width: 260px; }
.stCodeBlock, pre {
    border-radius: 12px !important;
    background-color: #2b2b2b !important;
}
.stCodeBlock code, pre code {
    color: #e8e6e0 !important;
}
</style>
""", unsafe_allow_html=True)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

if "history" not in st.session_state:
    st.session_state.history = load_history()
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "transcript" not in st.session_state:
    st.session_state.transcript = None

with st.sidebar:
    st.markdown("### 🎙️ Still")
    st.write("")
    for item in ["Home", "Insights", "Dictionary", "Settings"]:
        is_active = st.session_state.page == item
        if st.button(item, key=f"nav_{item}", type="primary" if is_active else "secondary"):
            st.session_state.page = item
            st.rerun()

def page_home():
    st.title("Dictation, kept here.")
    st.caption("Je opnames blijven lokaal op je eigen pc. Klik op een transcript om te kopiëren.")

    with st.container(border=True):
        col_a, col_b = st.columns([1, 1])

        with col_a:
           if not st.session_state.transcript:
                st.markdown("#### 〜 Your first thought can start anywhere.")
                st.write("Neem iets op, Still bewaart de transcriptie lokaal voor je.")

            audio_bytes = audio_recorder(
                text="Start opname",
                recording_color="#e74c3c",
                neutral_color="#4d8b7f",
                icon_size="2x",
                key="recorder",
            )

            transcribe_clicked = False
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                c1, c2, c3 = st.columns(3)
                with c1:
                    transcribe_clicked = st.button("Transcribeer", type="primary")
                with c2:
                    st.download_button("Download audio", data=audio_bytes,
                                        file_name="opname.wav", mime="audio/wav")
                with c3:
                    if st.button("Opnieuw opnemen"):
                        st.session_state.transcript = None
                        st.rerun()

                if transcribe_clicked:
                    with open(os.path.join(DATA_DIR, "temp_recording.wav"), "wb") as f:
                        f.write(audio_bytes)
                    with st.spinner("Model laden en transcriberen (lokaal)..."):
                        model = WhisperModel("small", device="cpu", compute_type="int8")
                        segments, info = model.transcribe(
    os.path.join(DATA_DIR, "temp_recording.wav"),
    language="nl",
    initial_prompt="Dit is een dictation-app genaamd Still. Veelgebruikte woorden: Alopias, Streamlit, GitHub, Whisper, Ollama."
)
                        text = "".join([s.text for s in segments]).strip()
                        st.session_state.transcript = text
                        entry = {"timestamp": datetime.now().strftime("%d-%m-%Y %H:%M"), "text": text}
                        st.session_state.history.insert(0, entry)
                        save_history(st.session_state.history)

            if st.session_state.transcript:
                st.subheader("Transcriptie")
                st.code(st.session_state.transcript, language=None)

        with col_b:
            st.markdown("#### Recent")
            if not st.session_state.history:
                st.caption("Nog geen opnames. Je eerste transcript verschijnt hier.")
            else:
                for entry in st.session_state.history[:8]:
                    st.caption(entry["timestamp"])
                    st.code(entry["text"], language=None)

def page_insights():
    st.title("Insights")
    st.caption("Een klein overzicht van je gebruik.")
    with st.container(border=True):
        total = len(st.session_state.history)
        total_words = sum(len(e["text"].split()) for e in st.session_state.history)
        c1, c2 = st.columns(2)
        c1.metric("Aantal opnames", total)
        c2.metric("Totaal aantal woorden", total_words)

def page_dictionary():
    st.title("Dictionary")
    st.caption("Eigen woorden/termen die je vaak gebruikt (lokaal opgeslagen).")
    dict_file = os.path.join(DATA_DIR, "dictionary.json")
    terms = json.load(open(dict_file, "r", encoding="utf-8")) if os.path.exists(dict_file) else []

    with st.container(border=True):
        new_term = st.text_input("Nieuwe term toevoegen")
        if st.button("Toevoegen", type="primary") and new_term:
            terms.append(new_term)
            with open(dict_file, "w", encoding="utf-8") as f:
                json.dump(terms, f, ensure_ascii=False, indent=2)
            st.rerun()
        if terms:
            for t in terms:
                st.write(f"• {t}")
        else:
            st.caption("Nog geen termen toegevoegd.")

def page_settings():
    st.title("Settings")
    with st.container(border=True):
        st.selectbox("Taal voor transcriptie", ["Nederlands", "English"], index=0)
        st.selectbox("Whisper-model", ["base", "small", "medium"], index=0,
                      help="Groter model = nauwkeuriger, maar trager.")
        if st.button("Geschiedenis wissen"):
            st.session_state.history = []
            save_history([])
            st.rerun()

pages = {"Home": page_home, "Insights": page_insights, "Dictionary": page_dictionary, "Settings": page_settings}
pages[st.session_state.page]()