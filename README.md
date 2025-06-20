# Audio Translation Pipeline

A speech-to-text → machine translation → text-to-speech pipeline with latency measurement and UI.

## 📁 Structure

- `app.py`: Core backend server (STT, MT, TTS, logging).
- `test.py`: Batch runner over all audio files.
- `ui.py`: Desktop UI for interactive use.
- `pipeline.py`: Performance measurement and plotting.
- `requirements.txt`: Dependencies.
- `dataset/`: Your audio dataset and reference text files.

## 🚀 Setup

```bash
git clone <your-repo-url>
cd audio-translation-pipeline
python -m venv venv
venv\Scripts\activate      # Windows
# or source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
