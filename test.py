import os, time, requests

BASE = "http://127.0.0.1:5000"
audio_dir = "dataset/audio"

for fname in os.listdir(audio_dir):
    if not fname.lower().endswith(".wav"):
        continue
    utt = os.path.splitext(fname)[0]
    print(f"\n=== Processing: {utt} ===")
    resp1 = requests.get(f"{BASE}/stt?file={fname}")
    print("STT →", resp1.status_code, resp1.json())
    if resp1.ok:
        txt = resp1.json().get("transcript","")
        resp2 = requests.post(f"{BASE}/mt", json={"utt_id":utt,"text":txt})
        print("MT →", resp2.status_code, resp2.json())
        if resp2.ok:
            trans = resp2.json().get("translation","")
            resp3 = requests.post(f"{BASE}/tts", json={"text":trans})
            print("TTS →", resp3.status_code, "Latency:", resp3.headers.get("X-TTS-Latency"))
            if resp3.ok:
                with open(f"out_{utt}.wav","wb") as f:
                    f.write(resp3.content)
                print(f"Saved audio: out_{utt}.wav")
