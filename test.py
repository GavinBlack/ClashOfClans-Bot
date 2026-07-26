from humancursor import SystemCursor
import pyautogui, random, time, keyboard, mouse
import numpy as np
import easyocr
from PIL import Image
from PIL import ImageEnhance
import pyscreeze


def rgb_to_hex(rgb):
    """Convert (R, G, B) → 'rrggbb' HEX string."""
    return '{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def check_colors(bothFound=False, forWalls=False, whichOne=1):
    targetStorages = [
        ((2117, 120), "e7c00d"),
        ((2112, 224), "c027c0")
    ]

    goldNumber = [
        ((1398, 1045), "ff887f")
    ]
    elixirNumber = [
        ((1587, 1041), "ff887f")
    ]
    redNumberFound = False
    
    if not forWalls:
        for (x, y), expected_hex in targetStorages:
            pixel = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
            pixel_hex = rgb_to_hex(pixel)

            print(f"Checking ({x}, {y}) → #{pixel_hex.upper()}")

            if pixel_hex.lower() == expected_hex.lower():

                bothFound = True
                print(f"✔ MATCH — Expected #{expected_hex}")
                redNumberFound = True
            else:
                print(f"✘ NO MATCH — Expected #{expected_hex}, got #{pixel_hex}")
            print()

        return bothFound
    else:
        if whichOne == 1:
            for (x, y), expected_hex in goldNumber:
                pixel = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
                pixel_hex = rgb_to_hex(pixel)

                print(f"Checking ({x}, {y}) → #{pixel_hex.upper()}")

                if pixel_hex.lower() == expected_hex.lower():
                    print(f"✔ MATCH — Expected #{expected_hex}")
                    redNumberFound = True
                else:
                    print(f"✘ NO MATCH — Expected #{expected_hex}, got #{pixel_hex}")
                print()
        else:
            for (x, y), expected_hex in elixirNumber:
                pixel = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
                pixel_hex = rgb_to_hex(pixel)

                print(f"Checking ({x}, {y}) → #{pixel_hex.upper()}")

                if pixel_hex.lower() == expected_hex.lower():
                    print(f"✔ MATCH — Expected #{expected_hex}")
                    redNumberFound = True
                else:
                    print(f"✘ NO MATCH — Expected #{expected_hex}, got #{pixel_hex}")
                print()
        return redNumberFound
    
bothFound = False
bothFound = check_colors(bothFound)