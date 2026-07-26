import pyautogui
import random
import time
from humancursor import SystemCursor

pyautogui.FAILSAFE = True  # Move mouse to top-left to stop

cursor = SystemCursor()

# -----------------------------
# CONFIG
# -----------------------------

ICON_IMAGES = [
    r"pics\darkElixirIcon.png",
    r"pics\elixirIcon.png"
]

ICON_CONFIDENCE = 0.75
END_CONFIDENCE = 0.8

X_MIN, X_MAX = 750, 2000
Y_MIN, Y_MAX = 250, 900

TOTAL_RUNTIME = 30  # seconds

# -----------------------------
# HELPERS
# -----------------------------

def human_pause(a=0.1, b=0.5):
    time.sleep(random.uniform(a, b))

def move_human(x, y):
    cursor.move_to([x, y])

def random_point():
    return random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX)

def small_drag():
    dx = random.randint(-80, 80)
    dy = random.randint(-80, 80)

    pyautogui.mouseDown()
    cur = pyautogui.position()
    cursor.move_to([cur.x + dx, cur.y + dy])
    pyautogui.mouseUp()

def maybe_click():
    if random.random() < 0.35:
        human_pause(0.05, 0.2)
        pyautogui.click()

def maybe_zoom():
    if random.random() < 0.40:
        direction = random.choice([1, -1])
        steps = random.randint(1, 3)
        for _ in range(steps):
            pyautogui.scroll(200 * direction)
            human_pause(0.05, 0.15)

# -----------------------------
# PRE-ZOOM OUT
# -----------------------------

def zoom_out_completely():
    w, h = pyautogui.size()
    cx, cy = w // 2, h // 2

    print("Centering cursor and zooming out...")
    move_human(cx, cy)
    human_pause(0.2, 0.4)

    for _ in range(random.randint(12, 18)):
        pyautogui.scroll(-300)
        human_pause(0.05, 0.12)

# -----------------------------
# ICON COLLECTION
# -----------------------------

def collect_icons():
    print("Searching for resource icons...")

    for icon in ICON_IMAGES:
        try:
            loc = pyautogui.locateOnScreen(icon, confidence=ICON_CONFIDENCE)
        except Exception:
            loc = None

        if loc:
            c = pyautogui.center(loc)
            print(f"Found {icon}, collecting...")
            move_human(c.x, c.y)
            human_pause(0.1, 0.3)
            pyautogui.click()
            human_pause(0.3, 0.6)
        else:
            print(f"{icon} not found.")

# -----------------------------
# END SEQUENCE (20% chance)
# -----------------------------

def end_sequence():
    print("Running end-of-program sequence...")

    # Step 1: random click in given range
    x = random.randint(230, 266)
    y = random.randint(93, 123)
    move_human(x, y)
    human_pause(0.1, 0.3)
    pyautogui.click()

    time.sleep(1.0)

    # Step 2: find myClan.png
    try:
        loc = pyautogui.locateOnScreen(r"pics\myClan.png", confidence=END_CONFIDENCE)
    except Exception:
        loc = None

    if loc:
        c = pyautogui.center(loc)
        move_human(c.x, c.y)
        human_pause(0.2, 0.4)
        pyautogui.click()

        # move down 150–300 px
        down = random.randint(250, 400)
        move_human(c.x, c.y + down)
        human_pause(0.2, 0.4)

        # scroll 3–13 times
        for _ in range(random.randint(3, 23)):
            pyautogui.scroll(-300)
            human_pause(0.05, 0.15)

    # Step 3: find and click x.png
    try:
        loc_x = pyautogui.locateOnScreen(r"pics\x.png", confidence=END_CONFIDENCE)
    except Exception:
        loc_x = None

    if loc_x:
        c2 = pyautogui.center(loc_x)
        move_human(c2.x, c2.y)
        human_pause(0.1, 0.3)
        pyautogui.click()

    print("End sequence complete.")

# -----------------------------
# MAIN
# -----------------------------

def main():
    print("Starting in 3 seconds... Move mouse to top-left to stop.")
    time.sleep(3)

    # 80% chance to NOT run
    if random.random() > 0.20:
        print("Decided not to run this time (80% chance). Exiting.")
        return

    print("Running behavior simulation (20% chance hit).")

    start_time = time.time()

    zoom_out_completely()
    collect_icons()

    # Human-like movement phase
    while time.time() - start_time < TOTAL_RUNTIME:
        x, y = random_point()
        move_human(x, y)
        human_pause(0.1, 0.4)

        if random.random() < 0.6:
            small_drag()
            human_pause(0.1, 0.4)

        maybe_click()
        maybe_zoom()

        if random.random() < 0.15:
            human_pause(1.0, 2.0)
        else:
            human_pause(0.3, 0.8)

    # 20% chance to run end sequence
    if random.random() < 0.20:
        end_sequence()
    else:
        print("Skipping end sequence (80% chance).")

    print("Done. Program finished.")

if __name__ == "__main__":
    main()
