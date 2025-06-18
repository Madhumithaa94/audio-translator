import time, os
from flask import Flask, request, jsonify, send_file
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment

# Ensure pydub locates ffmpeg correctly (Windows)
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"

app = Flask(__name__)
recognizer = sr.Recognizer()

@app.route('/stt', methods=['GET'])
def stt():
    path = r"C:\Users\Abcom\Downloads\harvard_16k_mono.wav"
    start = time.time()
    with sr.AudioFile(path) as src:
        audio = recognizer.record(src)
    t1 = time.time()
    try:
        text = recognizer.recognize_google(audio)
    except Exception:
        text = ""
    t2 = time.time()
    return jsonify({
        "transcript": text,
        "timings": {
            "record_seconds": t1 - start,
            "recognize_seconds": t2 - t1,
            "total_seconds": t2 - start
        }
    })

@app.route('/mt', methods=['POST'])
def mt():
    txt = request.get_json().get("text","").strip()
    if not txt:
        return jsonify(error="Missing 'text'"), 400
    start = time.time()
    try:
        translation = GoogleTranslator(source='auto', target='zh-CN').translate(txt)
    except Exception as e:
        return jsonify(error=str(e)), 500
    t1 = time.time()
    return jsonify({
        "translation": translation,
        "timings": {"mt_seconds": t1 - start}
    })

@app.route('/tts', methods=['POST'])
def tts():
    txt = request.get_json().get("text","").strip()
    if not txt:
        return jsonify(error="Missing 'text'"), 400

    start = time.time()
    tts = gTTS(text=txt, lang="zh-CN")
    tts.save("speech.mp3")
    AudioSegment.from_mp3("speech.mp3").export("speech.wav", format="wav")
    t2 = time.time()

    resp = send_file("speech.wav", mimetype="audio/wav",
                     as_attachment=True, download_name="speech.wav")
    resp.headers["X-TTS-Latency"] = str(t2 - start)
    return resp

@app.route('/')
def index():
    # Minimal UI interface inside the desktop window
    return '''
    <html><body>
      <h1>Audio Translator</h1>
      <button onclick="runPipeline()">Run Pipeline</button>
      <pre id="output"></pre>
      <script>
      async function runPipeline() {
        const out = document.getElementById('output');
        out.textContent = "Running...\\n";
        const stt = await fetch('/stt').then(r => r.json());
        out.textContent += "STT → "+JSON.stringify(stt, null,2)+"\\n";
        const mt = await fetch('/mt', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({text: stt.transcript})
        }).then(r => r.json());
        out.textContent += "MT → "+JSON.stringify(mt, null,2)+"\\n";
        const ttsResp = await fetch('/tts', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({text: mt.translation})
        });
        out.textContent += "TTS latency: "+ttsResp.headers.get('X-TTS-Latency')+"s\\n";
        const blob = await ttsResp.blob();
        const url = URL.createObjectURL(blob);
        new Audio(url).play();
      }
      </script>
    </body></html>
    '''

if __name__ == "__main__":
    app.run(debug=True)
