import os, time, csv
import speech_recognition as sr
from deep_translator import GoogleTranslator
from jiwer import wer
import sacrebleu
import numpy as np
import matplotlib.pyplot as plt

# Config
AUDIO_DIR = r"C:\Users\Abcom\Desktop\PROJECT002\dataset\audio"
TRANS = r"C:\Users\Abcom\Desktop\PROJECT002\dataset\transcript.txt"
TRANSL = r"C:\Users\Abcom\Desktop\PROJECT002\dataset\translation.txt"
CSV_OUT = r"C:\Users\Abcom\Desktop\PROJECT002\stats_output.csv"

# Load references
ref_asr = dict(line.strip().split("\t",1) for line in open(TRANS, "r", encoding="utf‑8"))
ref_mt = dict(line.strip().split("\t",1) for line in open(TRANSL, "r", encoding="utf‑8"))

recognizer = sr.Recognizer()
rows = []

print("\n📊 Processing audio files:")
print(f"{'Utterance':20s} | {'STT(s)':>7s} | {'MT(s)':>7s} | {'WER':>5s} | {'chrF':>5s}")
print("-"*60)

for fname in sorted(os.listdir(AUDIO_DIR)):
    utt, ext = os.path.splitext(fname)
    if ext.lower() != ".wav":
        continue

    gt_st = ref_asr.get(utt)
    gt_tr = ref_mt.get(utt)

    t0 = time.time()
    with sr.AudioFile(os.path.join(AUDIO_DIR, fname)) as src:
        audio = recognizer.record(src)
    hyp_st = recognizer.recognize_google(audio) if gt_st is not None else ""
    t_st = time.time() - t0

    t1 = time.time()
    hyp_tr = GoogleTranslator(source="auto", target="zh-CN").translate(hyp_st) if gt_tr is not None else ""
    t_mt = time.time() - t1

    wr = wer(gt_st, hyp_st) if gt_st else None
    ch = sacrebleu.corpus_chrf([hyp_tr], [[gt_tr]]).score if gt_tr else None

    rows.append({"utt": utt, "stt": t_st, "mt": t_mt, "wer": wr, "chrf": ch})
    print(f"{utt:20s} | {t_st:7.2f} | {t_mt:7.2f} | {wr or 0:5.3f} | {ch or 0:5.1f}")

# Save stats
with open(CSV_OUT, "w", newline="", encoding="utf‑8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print(f"\n✅ CSV saved at: {CSV_OUT}\n")

# Plot 1: Latency line
utts = [r["utt"] for r in rows]
stt_t = [r["stt"] for r in rows]
mt_t = [r["mt"] for r in rows]

plt.figure(figsize=(9,4))
plt.plot(utts, stt_t, "o-", label="STT (s)", color="blue")
plt.plot(utts, mt_t, "s-", label="MT (s)", color="orange")
plt.title("📈 Per‑Utterance Latency")
plt.xlabel("Utterance")
plt.ylabel("Time (s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot 2: Pie chart per file
for r in rows:
    plt.figure(figsize=(5,5))
    plt.pie([r["stt"], r["mt"]], labels=["STT","MT"], autopct="%1.1f%%",
            startangle=90, colors=["#6699CC","#FFCC66"])
    plt.title(f"⏱ Time distribution: {r['utt']}")
    plt.tight_layout()
    plt.show()
