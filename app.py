import os, time
from flask import Flask, request, jsonify, send_file
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment

AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
app = Flask(__name__)
recognizer = sr.Recognizer()

def log_transcript(utt_id, text):
    os.makedirs("dataset", exist_ok=True)
    with open("dataset/transcript.txt","a",encoding="utf‑8") as f:
        f.write(f"{utt_id}\t{text}\n")

def log_translation(utt_id, text):
    os.makedirs("dataset", exist_ok=True)
    with open("dataset/translation.txt","a",encoding="utf‑8") as f:
        f.write(f"{utt_id}\t{text}\n")

@app.route('/list_audio')
def list_audio():
    files = [f for f in os.listdir("dataset/audio") if f.lower().endswith(".wav")]
    return jsonify(files)

@app.route('/stt', methods=['GET'])
def stt():
    fname = request.args.get("file")
    if not fname: return jsonify(error="Missing 'file' query param"), 400
    path = os.path.join("dataset","audio",fname)
    if not os.path.isfile(path): return jsonify(error="File not found"),404
    utt = os.path.splitext(fname)[0]
    t0 = time.time()
    with sr.AudioFile(path) as src:
        audio = recognizer.record(src)
    t1 = time.time()
    try:
        text = recognizer.recognize_google(audio)
    except:
        text = ""
    t2 = time.time()
    log_transcript(utt, text)
    return jsonify({
        "utt_id": utt,
        "transcript": text,
        "timings": {
            "record": round(t1-t0,3),
            "recognize": round(t2-t1,3),
            "total": round(t2-t0,3)
        }
    })

@app.route('/mt', methods=['POST'])
def mt():
    data = request.get_json()
    utt = data.get("utt_id","unknown")
    txt = data.get("text","").strip()
    if not txt: return jsonify(error="Missing 'text'"),400
    t0 = time.time()
    translation = GoogleTranslator(source="auto", target="zh-CN").translate(txt)
    t1 = time.time()
    log_translation(utt, translation)
    return jsonify({"utt_id": utt, "translation": translation,
                    "timings": {"mt": round(t1-t0,3)}})

@app.route('/tts', methods=['POST'])
def tts():
    txt = request.get_json().get("text","").strip()
    if not txt: return jsonify(error="Missing 'text'"),400
    t0 = time.time()
    tts = gTTS(text=txt, lang="zh-CN")
    tts.save("speech.mp3")
    AudioSegment.from_mp3("speech.mp3").export("speech.wav", format="wav")
    t1 = time.time()
    resp = send_file("speech.wav", mimetype="audio/wav",
                     as_attachment=True, download_name="speech.wav")
    resp.headers["X-TTS-Latency"] = str(round(t1-t0,3))
    return resp

@app.route('/')
def index():
    return '''
<html><body>
  <h1>Audio Translator</h1>
  <label>Select audio:</label>
  <select id="fileSelect"></select>
  <button onclick="runPipeline()">Run Pipeline</button>
  <pre id="output"></pre>
  <script>
    async function loadFiles() {
      const sel = document.getElementById('fileSelect');
      const files = await fetch('/list_audio').then(r=>r.json());
      files.forEach(f=>{
        const o = new Option(f,f);
        sel.add(o);
      });
    }
    async function runPipeline() {
      const out = document.getElementById('output');
      const file = document.getElementById('fileSelect').value;
      if(!file)return alert("Select a file.");
      out.textContent = "Running...\\n";
      const stt = await fetch('/stt?file='+encodeURIComponent(file)).then(r=>r.json());
      out.textContent += "STT → "+JSON.stringify(stt,null,2)+"\\n";
      const mt = await fetch('/mt', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({utt_id:stt.utt_id, text: stt.transcript})
      }).then(r=>r.json());
      out.textContent += "MT → "+JSON.stringify(mt,null,2)+"\\n";
      const tts = await fetch('/tts', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({text: mt.translation})
      });
      out.textContent += "TTS latency: "+tts.headers.get('X-TTS-Latency')+"s\\n";
      const blob = await tts.blob();
      new Audio(URL.createObjectURL(blob)).play();
    }
    loadFiles();
  </script>
</body></html>
'''

if __name__ == "__main__":
    app.run(debug=True)
