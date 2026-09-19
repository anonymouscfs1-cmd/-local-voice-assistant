from faster_whisper import WhisperModel

def transcribe(audio_path="data/recording.wav"):
    model = WhisperModel("base", device="cpu", compute_type="int8")

    segments, info = model.transcribe(audio_path, language="nl")

    print(f"Gedetecteerde taal: {info.language} (kans: {info.language_probability:.2f})")
    full_text = ""
    for segment in segments:
        full_text += segment.text
    print("Transcriptie:", full_text.strip())
    return full_text

if __name__ == "__main__":
    transcribe()