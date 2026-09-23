import keyboard
import pyperclip
from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile

SAMPLE_RATE = 16000
model = WhisperModel("small", device="cpu", compute_type="int8")

def record_and_transcribe():
    frames = []
    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    print("Opname gestart (laat Ctrl+Shift+Space los om te stoppen)...")
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback)
    stream.start()

    keyboard.wait("ctrl+shift+space", suppress=False)  # wacht tot je loslaat
    stream.stop()

    audio = np.concatenate(frames, axis=0)
    wavfile.write("data/hotkey_recording.wav", SAMPLE_RATE, audio)

    segments, info = model.transcribe("data/hotkey_recording.wav", language="nl")
    text = "".join([s.text for s in segments]).strip()

    pyperclip.copy(text)  # naar klembord, plak zelf met Ctrl+V waar je maar wilt
    print("Getranscribeerd en gekopieerd:", text)

print("Klaar. Houd Ctrl+Shift+Space ingedrukt om op te nemen.")
keyboard.add_hotkey("ctrl+shift+space", record_and_transcribe, suppress=True, trigger_on_release=False)
keyboard.wait()