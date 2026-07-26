from humancursor import SystemCursor
import pyautogui, random, time, keyboard, mouse
import numpy as np
import easyocr
from PIL import Image
from PIL import ImageEnhance
import pyscreeze

pyautogui.FAILSAFE = False
confidence = 0.75
tolerance = 5

# Initialize a "human-like" cursor
cursor = SystemCursor()

# Small offset for randomized cursor movement
num = 0.0


def find_with_scroll(image_path, max_attempts=20, scroll_amount=-5, pause_between=0.1, confidence=0.85):
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

        time.sleep(4)

        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except:
            continue

        if location is not None:
            return location

    return None

def checkLootTotal():
    """
    Screenshots the gold and elixir amounts, reads them using OCR, 
    and decides whether to continue or move to the next match.
    """
    reader = easyocr.Reader(['en'])
    time.sleep(2)

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

        print(goldAmount, elixirAmount)

        totalLoot = goldAmount + elixirAmount

        # If loot is below threshold, click 'Next'
        if totalLoot < 1000000:
            #print("total", totalLoot)

            # This will continuously search until next.png is found
            x, y = locateOnScreen(r"pics\next.png")

            # click it once found
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click(x, y)
            time.sleep(4)
        else:
            # Enough loot collected; stop looping
            time.sleep(3)
            break

def doMovements(path):
    """
    Move the cursor to a target image on the screen in a 'human-like' manner and click it.

    Args:
        path (str): Filepath to the image to locate and click.
    """
    x, y = locateOnScreen(path)  # Locate x, y coordinates
    cursor.move_to([x + num + 10, y - num - 10])  # Move cursor in a human-like manner
    pyautogui.click()  # Click at the location


def locateOnScreen_timeout(path, timeout=6, confidence=0.80):
    """Try to locate an image on screen but give up after `timeout` seconds.

    Returns (x, y) center coordinates if found, otherwise returns None.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            loc = pyautogui.locateOnScreen(path, confidence=confidence)
        except Exception as e:
            print(f"locateOnScreen_timeout exception for {path}: {e}")
            loc = None

        if loc is not None:
            center = pyautogui.center(loc)
            return center.x, center.y

        time.sleep(0.2)

    return None

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
            location = pyautogui.locateOnScreen(path, confidence=0.80)
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

def rgb_to_hex(rgb):
    """Convert (R, G, B) → 'rrggbb' HEX string."""
    return '{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def check_colors(bothFound=False, forWalls=False, whichOne=1):
    targetStorages = [
        ((2117, 120), "cba90b"),
        ((2112, 224), "a922a9")
    ]

    goldNumber = [
        ((1394, 1039), "e07770"),
        ((1468, 1037), "e07770")
    ]
    elixirNumber = [
        ((1587, 1039), "e07770"),
        ((1659, 1039), "e07770")
    ]
    redNumberFound = False
    
    if not forWalls: 
        bothFound = True  # assume true, only turn false if any fail

        for (x, y), expected_hex in targetStorages:
            pixel = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
            pixel_hex = rgb_to_hex(pixel)

            if pixel_hex.lower() != expected_hex.lower():
                bothFound = False

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
            return redNumberFound

def findWordWallsWithScrolling():
    scroll_image = r"pics\wallWord.png"
    loc = find_with_scroll(scroll_image,
                        max_attempts=30,
                        scroll_amount=-5,   # smaller scroll per attempt
                        pause_between=0.15,
                        confidence=0.92)

    if loc:
        center = pyautogui.center(loc)
        # Optionally click
        pyautogui.moveTo(center)
        pyautogui.click()
    else:
        print("Image not found after scrolling attempts.")

def checkIfMaxLoot():
    clicks = 12
    bothFound = False 
    redNumberFound = False
    onlyOneWall = False
    lessThan10Walls = False
    #time.sleep(5)  # TEMPORARY NOTHING
    bothFound = check_colors(bothFound)

    if bothFound:
              
        doMovements(r"pics\builderFace.png")

        time.sleep(.2)
        
        pyautogui.moveTo(1351,512)
        time.sleep(.2)

        findWordWallsWithScrolling()  

        time.sleep(1)

        try:
            redUpgrade = pyautogui.locateOnScreen(r"pics\redUpgrade.png", confidence=0.95)
            if redUpgrade is not None:
                onlyOneWall = True
        except:
            pass

        if not onlyOneWall:
            time.sleep(.3)
            doMovements(r"pics\upgradeMore.png")

            time.sleep(2)
            
            searchFor10LocationAndReact()

            for _ in range(clicks):
                pyautogui.click()
                time.sleep(.5)
                redNumberFound = check_colors(forWalls=True)
                if redNumberFound:
                    print('found the red number')
                    print('trying to hit remove first time')
                    doMovements(r"pics\remove.png")
                    time.sleep(1)
                    break
                time.sleep(.2)

            doMovements(r"pics\upgrade.png")
            #doMovements(r"pics\okayWalls.png") 
            doMovements(r"pics\cancel.png") 
            doMovements(r"pics\builderFace.png")

            time.sleep(.2)
            pyautogui.moveTo(1351,512)
            time.sleep(.2)

            findWordWallsWithScrolling()

            doMovements(r"pics\upgradeMore.png")

            searchFor10LocationAndReact()

            time.sleep(2)

            for _ in range(clicks):
                pyautogui.click()
                time.sleep(.5)
                redNumberFound = check_colors(forWalls=True, whichOne=2)
                if redNumberFound:
                    print('found the red number')
                    print('trying to hit remove first time')
                    doMovements(r"pics\remove.png")
                    #redNumberFound = check_colors(forWalls=True, whichOne=2)
                    time.sleep(1)
                    break
                time.sleep(.2)

            upgrade_x, upgrade_y = locateOnScreen(r"pics\upgrade.png")
            pyautogui.moveTo(upgrade_x+200, upgrade_y)
            pyautogui.click(upgrade_x+200, upgrade_y)
            #doMovements(r"pics\okayWalls.png")
            doMovements(r"pics\cancel.png") 
        else:
            print(onlyOneWall)
            upgrade_x, upgrade_y = locateOnScreen(r"pics\upgrade.png")
            pyautogui.moveTo(upgrade_x+200, upgrade_y)
            pyautogui.click(upgrade_x+200, upgrade_y)
            time.sleep(.5)
            doMovements(r"pics\confirm.png")
            time.sleep(.5)

def searchFor10LocationAndReact():
    tenLocation = None

    try:
        tenLocation = pyautogui.locateOnScreen(r"pics\10.png", confidence=.98)
        print(f"locateOnScreen returned: {tenLocation}")
    except Exception as e:
        # Don't silently ignore errors; treat as not found and print the exception for debugging
        print(f"locateOnScreen exception: {e}")
        tenLocation = None

    if tenLocation is not None:
        ten_x, ten_y = pyautogui.center(tenLocation)
        pyautogui.moveTo(ten_x+200,ten_y)
    else:
        addWall = locateOnScreen_timeout(r"pics\addWall.png", timeout=6, confidence=0.85)
        if addWall is None:
            print("upgrade button not found; skipping upgrades")
        else:
            addWall_x, addWall_y = addWall
            pyautogui.moveTo(addWall_x, addWall_y)



while True:
        checkIfMaxLoot()

        

main()