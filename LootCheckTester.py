import time
import random
import numpy as np
import pyautogui
import easyocr
from PIL import ImageEnhance

# -----------------------------
# CONFIG
# -----------------------------

GOLD_REGION   = (261, 194, 179, 35)
ELIXIR_REGION = (256, 257, 178, 31)

OCR_CONFIDENCE_MIN = 0.55
LOOP_DELAY = 0.3

# -----------------------------
# INIT OCR
# -----------------------------

reader = easyocr.Reader(['en'], gpu=True)

# -----------------------------
# OCR NUMBER READER
# -----------------------------

def read_loot_number(region):
    screenshot = pyautogui.screenshot(region=region)

    img = screenshot.convert("L")

    # Upscale to help thin digits like '1'
    img = img.resize((img.width * 2, img.height * 2))

    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Sharpness(img).enhance(2.0)

    img_np = np.array(img)

    results = reader.readtext(
        img_np,
        allowlist="0123456789",
        paragraph=False
    )

    if not results:
        return 0

    pieces = []

    for box, text, conf in results:
        if conf < OCR_CONFIDENCE_MIN:
            continue

        digits = "".join(c for c in text if c.isdigit())
        if digits:
            x_positions = [p[0] for p in box]
            pieces.append((min(x_positions), digits))

    if not pieces:
        return 0

    # Sort left → right and combine
    pieces.sort(key=lambda x: x[0])
    number = int("".join(p[1] for p in pieces))

    return number

# -----------------------------
# MAIN LOOP
# -----------------------------

time.sleep(random.uniform(2.0, 3.0))

while True:
    gold   = read_loot_number(GOLD_REGION)
    elixir = read_loot_number(ELIXIR_REGION)

    total = gold + elixir

    print(f"Gold: {gold}, Elixir: {elixir}, Total: {total}")

    time.sleep(LOOP_DELAY)
