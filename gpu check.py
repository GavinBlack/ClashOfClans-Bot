import time
import random
import numpy as np
import pyautogui
import easyocr
from PIL import ImageEnhance

reader = easyocr.Reader(['en'])
time.sleep(random.uniform(2.0, 3.0))

while True:
    # Take screenshots of gold and elixir areas
    goldScreenshot = pyautogui.screenshot(region=(257, 186, 186, 50))
    elixirScreenshot = pyautogui.screenshot(region=(245, 251, 209, 41))

    # Convert to grayscale
    goldImage = goldScreenshot.convert("L")
    elixirImage = elixirScreenshot.convert("L")

    # Enhance contrast
    contrastEnhancer = ImageEnhance.Contrast(goldImage)
    goldImage = contrastEnhancer.enhance(2.0)
    contrastEnhancer = ImageEnhance.Contrast(elixirImage)
    elixirImage = contrastEnhancer.enhance(2.0)

    # Enhance sharpness
    sharpnessEnhancer = ImageEnhance.Sharpness(goldImage)
    goldImage = sharpnessEnhancer.enhance(2.0)
    sharpnessEnhancer = ImageEnhance.Sharpness(elixirImage)
    elixirImage = sharpnessEnhancer.enhance(2.0)

    # Convert images to numpy arrays for OCR
    img_np_gold = np.array(goldImage)
    img_np_elixir = np.array(elixirImage)

    # OCR with digits only
    resultGold = reader.readtext(img_np_gold, allowlist='0123456789 ')
    resultElixir = reader.readtext(img_np_elixir, allowlist='0123456789 ')

    # Extract gold amount
    if resultGold:
        detected_text = resultGold[0][-2]
        goldAmount = int(detected_text.replace(' ', '') or 0)
    else:
        goldAmount = 0

    # Extract elixir amount
    if resultElixir:
        detected_text = resultElixir[0][-2]
        elixirAmount = int(detected_text.replace(' ', '') or 0)
    else:
        elixirAmount = 0

    #print(goldAmount, elixirAmount)

    totalLoot = goldAmount + elixirAmount
    print(f"Gold: {goldAmount}, elixir: {elixirAmount}")
    time.sleep(.3)