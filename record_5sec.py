import sounddevice as sd
import numpy as np
import scipy.io.wavfile

SAMPLE_RATE = 16000  # 16kHz
DURATION = 5  # 5초

def record_5_seconds(filename="record_5sec.wav"):
    print("🎙️ 5초간 녹음 시작...")
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    print("✅ 녹음 완료!")

    # 저장
    scaled = (audio.flatten() * 32767).astype(np.int16)
    scipy.io.wavfile.write(filename, SAMPLE_RATE, scaled)
    print(f"💾 저장됨: {filename}")

if __name__ == "__main__":
    record_5_seconds()