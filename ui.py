import threading, webview, time
from app import app

def start_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()
    time.sleep(0.5)
    webview.create_window("Audio Translator", "http://127.0.0.1:5000", width=800, height=600)
    webview.start()
