"""
MedForever Launcher Script
Starts the FastAPI server and launches the dashboard in default web browser.
"""
import sys
import webbrowser
import threading
import time

def open_browser(url: str):
    time.sleep(1.2)
    print(f"[*] Opening dashboard at {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    import uvicorn
    from backend.config import APP_HOST, APP_PORT

    url = f"http://{APP_HOST}:{APP_PORT}"
    print("=" * 65)
    print(" 🏥 MedForever - Universal Multimodal Medical Bridge")
    print(" Google for Developers | PromptWars x Techverse")
    print("=" * 65)
    print(f"[*] Server starting on: {url}")
    print("[*] Press CTRL+C to stop the server.\n")

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=False)
