import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile

SAMPLE_RATE = 16000

def record_audio():
    print("Druk op Enter om op te nemen...")
    input()
    print("Opname gestart, druk Enter om te stoppen...")

    frames = []
    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback)
    with stream:
        input()

    audio = np.concatenate(frames, axis=0)
    wavfile.write("data/recording.wav", SAMPLE_RATE, audio)
    print("Opname opgeslagen als data/recording.wav")

if __name__ == "__main__":
    record_audio()
