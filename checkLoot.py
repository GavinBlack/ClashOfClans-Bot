
from humancursor import SystemCursor
import pyautogui, random, time, keyboard, mouse
import numpy as np
import easyocr
from PIL import Image
def checkLootTotal():
    reader = easyocr.Reader(['en'])

    img = pyautogui.screenshot(region=(261, 197, 179, 32))
    img.show()



    while 1:  
        goldScreenshot = pyautogui.screenshot(region=(261, 189, 182, 40))
        elixirScreenshot = pyautogui.screenshot(region=(245, 251, 209, 41))

        goldImage = goldScreenshot.convert("RGB")
        elixirImage = elixirScreenshot.convert("RGB")


        img_np_gold = np.array(goldImage)
        img_np_elixir = np.array(elixirImage)

        resultGold = reader.readtext(img_np_gold)
        resultElixir = reader.readtext(img_np_elixir)

        detected_text = resultGold[0][-2]   # recognized text
        goldAmount = ''.join(filter(str.isdigit, detected_text))
        print(f"Detected number: {goldAmount}")
        detected_text = resultElixir[0][-2]   # recognized text
        elixirAmount = ''.join(filter(str.isdigit, detected_text))
        print(f"Detected number: {elixirAmount}")
checkLootTotal()