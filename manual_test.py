import os
import json
import time
import threading
import random
from datetime import datetime

import pyautogui
import keyboard as kb
from pynput import mouse
from pynput.keyboard import Controller

# =========================
# Keyboard controller (REPLAY)
# =========================
kbd = Controller()

# =========================
# PyAutoGUI settings
# =========================
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# =========================
# Paths
# =========================
JSON_DIR = "json"
JSON_PATH = os.path.join(JSON_DIR, "recordings_test.json")

# =========================
# Control keys
# =========================
START_KEY = 'v'
STOP_KEY = 'b'
REPLAY_KEY = 'n'
AUTO_REPLAY_KEY = 'g'
QUIT_KEY = 'm'

CONTROL_KEYS = {START_KEY, STOP_KEY, REPLAY_KEY, AUTO_REPLAY_KEY, QUIT_KEY}

# =========================
# Timing
# =========================
BUSYWAIT_SLEEP = 0.0005
KEY_DELAY = 0.003
TINY_OFFSET_PIXELS = 2
AUTO_REPLAY_DELAY = 1.0

# =========================
# Globals
# =========================
recording = False
replaying = False
running = True

events = []
events_lock = threading.Lock()
t0 = 0.0

# =========================
# JSON helpers
# =========================
def ensure_json():
    os.makedirs(JSON_DIR, exist_ok=True)
    if not os.path.exists(JSON_PATH):
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump({"recordings": []}, f, indent=2)

def load_data():
    ensure_json()
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        data = {"recordings": []}
        save_data(data)
        return data

def save_data(data):
    ensure_json()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =========================
# Timing
# =========================
def rel_time():
    return time.perf_counter() - t0

# =========================
# Mouse helpers
# =========================
def normalize_button(btn):
    s = str(btn).lower()
    if "right" in s:
        return "right"
    if "middle" in s:
        return "middle"
    return "left"

# =========================
# Mouse callbacks
# =========================
def on_move(x, y):
    if not recording or replaying:
        return
    with events_lock:
        events.append({"type": "move", "x": x, "y": y, "t": rel_time()})

def on_click(x, y, button, pressed):
    if not recording or replaying:
        return
    with events_lock:
        events.append({
            "type": "mouse",
            "action": "down" if pressed else "up",
            "x": x,
            "y": y,
            "button": normalize_button(button),
            "t": rel_time()
        })

def on_scroll(x, y, dx, dy):
    if not recording or replaying:
        return
    with events_lock:
        events.append({"type": "scroll", "dy": dy, "t": rel_time()})

# =========================
# Keyboard recording
# =========================
def record_key_event(e):
    if not recording or replaying:
        return

    key = (e.name or "").lower()
    if not key or key in CONTROL_KEYS:
        return

    with events_lock:
        events.append({
            "type": "key",
            "action": e.event_type,
            "key": key,
            "t": rel_time()
        })

# =========================
# Replay
# =========================
def replay_recording(index):
    global replaying
    time.sleep(1.5)

    data = load_data()
    recs = data["recordings"]

    if index < 0 or index >= len(recs):
        print("❌ Invalid recording index")
        return

    seq = recs[index]["events"]
    if not seq:
        print("❌ Empty recording")
        return

    print(f"🔁 Replaying #{index} ({len(seq)} events)")
    replaying = True

    try:
        start = time.perf_counter()

        for e in seq:
            while (time.perf_counter() - start) < e["t"]:
                time.sleep(BUSYWAIT_SLEEP)

            ox = random.randint(-TINY_OFFSET_PIXELS, TINY_OFFSET_PIXELS)
            oy = random.randint(-TINY_OFFSET_PIXELS, TINY_OFFSET_PIXELS)

            if e["type"] == "move":
                pyautogui.moveTo(e["x"] + ox, e["y"] + oy, duration=0)

            elif e["type"] == "mouse":
                x, y = e["x"] + ox, e["y"] + oy
                if e["action"] == "down":
                    pyautogui.mouseDown(x=x, y=y, button=e["button"])
                else:
                    pyautogui.mouseUp(x=x, y=y, button=e["button"])

            elif e["type"] == "scroll":
                from pynput.mouse import Controller as MouseController

                mouse_ctl = MouseController()

                # pynput scroll(dx, dy)
                # dy > 0 = wheel up, dy < 0 = wheel down
                mouse_ctl.scroll(0, e["dy"])


            elif e["type"] == "key":
                if e["action"] == "down":
                    kbd.press(e["key"])
                else:
                    kbd.release(e["key"])
                time.sleep(KEY_DELAY)

        print("✅ Replay finished")

    finally:
        replaying = False

# =========================
# Controls
# =========================
def start_recording():
    global recording, t0, events
    if replaying:
        return
    with events_lock:
        events = []
    t0 = time.perf_counter()
    recording = True
    print("▶ RECORDING STARTED")

def stop_recording():
    global recording
    if not recording:
        return
    recording = False

    data = load_data()
    with events_lock:
        snap = list(events)

    data["recordings"].append({
        "id": len(data["recordings"]),
        "created": datetime.now().isoformat(timespec="seconds"),
        "events": snap
    })
    save_data(data)

    print(f"⏹ SAVED ({len(snap)} events)")

def request_replay():
    if recording or replaying:
        return

    def prompt():
        data = load_data()
        for i, r in enumerate(data["recordings"]):
            print(f"#{i} | {r['created']} | {len(r['events'])} events")
        try:
            idx = int(input("Replay #: "))
            time.sleep(0.5)
            replay_recording(idx)
        except:
            print("❌ Invalid input")

    threading.Thread(target=prompt, daemon=True).start()

def auto_replay_last():
    if recording or replaying:
        return

    data = load_data()
    recs = data["recordings"]
    if not recs:
        print("❌ No recordings to replay")
        return

    last_index = len(recs) - 1
    print(f"⏱ Auto replaying last recording #{last_index} in 1 second")

    def delayed():
        time.sleep(AUTO_REPLAY_DELAY)
        replay_recording(last_index)

    threading.Thread(target=delayed, daemon=True).start()

def quit_program():
    global running
    running = False
    print("🛑 EXIT")

# =========================
# Main
# =========================
def main():
    ensure_json()

    print("🎮 Macro Recorder")
    print("v=start | b=stop | n=replay menu | g=auto replay last | m=quit")

    mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll).start()
    kb.hook(record_key_event)

    kb.add_hotkey(START_KEY, start_recording, suppress=True)
    kb.add_hotkey(STOP_KEY, stop_recording, suppress=True)
    kb.add_hotkey(REPLAY_KEY, request_replay, suppress=True)
    kb.add_hotkey(AUTO_REPLAY_KEY, auto_replay_last, suppress=True)
    kb.add_hotkey(QUIT_KEY, quit_program, suppress=True)

    while running:
        time.sleep(0.1)

    kb.unhook_all()
    print("Exited cleanly")

if __name__ == "__main__":
    main()
