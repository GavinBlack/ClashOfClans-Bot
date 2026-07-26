# 2216 118 for gold     2112 224 for elixir
#gold color e7c00d      elixir color c027c0

import pyautogui
import time

pyautogui.moveTo(2216, 118)


# Target coordinates and expected HEX values
targets = [
    ((2117, 120), "e7c00d"),
    ((2112, 224), "c027c0")
]

def rgb_to_hex(rgb):
    """Convert (R, G, B) → 'rrggbb' HEX string."""
    return '{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def locateOnScreen(path):
    """
    Locate an image on the screen and return its center coordinates (x, y).

    Args:
        path (str): Filepath to the image to locate.

    Returns:
        tuple: (x, y) center coordinates of the found image.
    """
    location = None
    while location is None:
        try:
            location = pyautogui.locateOnScreen(path, confidence=0.75)
        except Exception:
            # Sleep briefly if an error occurs and try again
            time.sleep(0.1)
            continue

        if location is None:
            # Image not found yet; wait and retry
            time.sleep(0.1)

    # Once found, get the center position
    center = pyautogui.center(location)
    x, y = center.x, center.y
    return x, y
num = 0.0
from humancursor import SystemCursor
import pyautogui, random, time, keyboard, mouse
import numpy as np
import easyocr
from PIL import Image
from PIL import ImageEnhance
import pyscreeze
cursor = SystemCursor()

def doMovements(path):
    """
    Move the cursor to a target image on the screen in a 'human-like' manner and click it.

    Args:
        path (str): Filepath to the image to locate and click.
    """
    x, y = locateOnScreen(path)  # Locate x, y coordinates
    cursor.move_to([x + num + 10, y - num - 10])  # Move cursor in a human-like manner
    pyautogui.click()  # Click at the location

def check_colors(bothFound):
    
    for (x, y), expected_hex in targets:
        pixel = pyautogui.screenshot().getpixel((x, y))
        pixel_hex = rgb_to_hex(pixel)

        print(f"Checking ({x}, {y}) → #{pixel_hex.upper()}")

        if pixel_hex.lower() == expected_hex.lower():
            print(f"✔ MATCH — Expected #{expected_hex}")
            bothFound = True
        else:
            print(f"✘ NO MATCH — Expected #{expected_hex}, got #{pixel_hex}")
        print()

    return bothFound

def find_with_scroll(image_path, max_attempts=20, scroll_amount=-5, pause_between=0.1, confidence=0.75):
    """
    Scrolls repeatedly and tries to locate the given image after each scroll step.
    Returns the location if found, or None if not found after max_attempts.

    Params:
      image_path (str): path to the image to locate.
      max_attempts (int): maximum number of scroll-and-try iterations.
      scroll_amount (int): amount of wheel scroll each iteration (negative => down).
      pause_between (float): seconds to wait after scrolling before locating.
      confidence (float): confidence threshold for image lookup.
    """
    for attempt in range(max_attempts):
        # do a small scroll
        mouse.wheel(scroll_amount)

        # wait a bit for screen to update
        time.sleep(pause_between)

        time.sleep(2.5)

        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except:
            continue

        if location is not None:
            return location

    return None

"""
        doMovements(r"pics\builderFace.png")

        time.sleep(.2)
        pyautogui.moveTo(1351,512)
        time.sleep(.2)

        findWordWallsWithScrolling()        

        time.sleep(.3)
        doMovements(r"pics\upgradeMore.png")
        time.sleep(.1)

        for _ in range(clicks):
            pyautogui.click()
            time.sleep(.2)

        doMovements(r"pics\upgrade.png")
        doMovements(r"pics\okayWalls.png")"""

if __name__ == "__main__":
    bothFound = False
    time.sleep(2)  # small delay for you to get ready
    bothFound = check_colors(bothFound)

    if bothFound:
        face = doMovements(r"pics\builderFace.png")
        print('moving to face')

        #1351 512
        time.sleep(.2)
        pyautogui.moveTo(1351,512)
        time.sleep(.2)

        # Usage example:
        scroll_image = r"pics\wallWord.png"
        loc = find_with_scroll(scroll_image,
                            max_attempts=30,
                            scroll_amount=-2,   # smaller scroll per attempt
                            pause_between=0.15,
                            confidence=0.80)

        if loc:
            center = pyautogui.center(loc)
            print("Found image at:", center)
            # Optionally click
            pyautogui.moveTo(center)
            pyautogui.click()
        else:
            print("Image not found after scrolling attempts.")


        clicks = 12




 """
        put  before the thing

doMovements(r"pics\builderFace.png")

        time.sleep(.2)
        pyautogui.moveTo(1351,512)
        time.sleep(.2)

        findWordWallsWithScrolling()        

        time.sleep(.3)
        doMovements(r"pics\upgradeMore.png")
        doMovements(r"pics\addWall.png")
        time.sleep(.5)

        for _ in range(clicks):
            pyautogui.click()
            redNumberFound = check_colors(forWalls=True)
            if redNumberFound:
                print('found the red number')
                break
            time.sleep(.55)

        doMovements(r"pics\upgrade.png")
        #doMovements(r"pics\okayWalls.png")  





        """





