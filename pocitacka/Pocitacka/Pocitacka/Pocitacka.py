import sounddevice as sd     # prvni
import queue
import json
from vosk import Model, KaldiRecognizer

# hlavni nastaveni, cesta k modelu
MODEL_PATH = "vosk-model-small-cs-0.4"  
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

# print - nacita se vosk, recognizer
q = queue.Queue()
print("🎧 Načítám český model VOSK...") 
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)

# vyber audio zarizeni (chcem input, takze mikrofon dle volby)
print("\n🎤 Dostupná audio zařízení:\n")
devices = sd.query_devices()
for i, d in enumerate(devices):
    print(f"{i}: {d['name']}")

device_index = int(input("\n🔢 Zadej číslo zařízení, které chceš poslouchat: "))
print(f"\n✅ Poslouchám z: {devices[device_index]['name']}\n")

# volej zpet "snad si vzpomenu"
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# hlavni cast pro fungovani
with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, device=device_index,
                       dtype='int16', channels=1, callback=callback):
    print("🗣️ Mluv – rozpoznaný text se zobrazí níže (Ctrl+C pro ukončení)\n")
    try:
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text.strip():
                    print(f"📝 {text}")
            else:
                partial = json.loads(rec.PartialResult()).get("partial", "")
                if partial.strip():
                    print(f"\r🎙️ {partial}", end="", flush=True)
    except KeyboardInterrupt:
        print("\n🛑 Ukončeno uživatelem.")
