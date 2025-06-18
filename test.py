import requests

resp1 = requests.get("http://127.0.0.1:5000/stt", timeout=30)
print("STT →", resp1.status_code, resp1.json())

if resp1.ok:
    txt = resp1.json().get("transcript","")
    resp2 = requests.post("http://127.0.0.1:5000/mt", json={"text":txt}, timeout=30)
    print("MT →", resp2.status_code, resp2.json())

    if resp2.ok:
        zh = resp2.json().get("translation","")
        resp3 = requests.post("http://127.0.0.1:5000/tts", json={"text":zh}, timeout=60)
        print("TTS →", resp3.status_code, "Latency:", resp3.headers.get("X-TTS-Latency"))
        if resp3.ok:
            with open("out.wav","wb") as f:
                f.write(resp3.content)
            print("Saved audio to out.wav")
