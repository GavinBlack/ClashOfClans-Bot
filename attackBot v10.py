"""

Clash of Clans Automation Script
Author: Gavin Black, 2025

This script automates various aspects of gameplay in the mobile game Clash of Clans.
It simulates human-like interactions to perform actions such as attacking bases,
deploying troops, collecting resources, and upgrading buildings.

The automation uses image recognition for UI element detection, OCR for reading
resource values, and randomized timings to mimic human behavior and avoid detection.

Dependencies:
- humancursor: For human-like cursor movements.
- pyautogui: For screen interactions and image location.
- easyocr: For optical character recognition on screenshots.
- PIL (Pillow): For image processing.
- numpy: For array operations in OCR.
- keyboard, mouse: For simulating key presses and mouse wheel.
- coords: Custom module containing coordinate lists.
- pyscreeze: For image location (used by pyautogui).

Usage:
Run the script while the Clash of Clans game is active on screen.
The script will prompt for whether to stop when storages are full.
It then enters a loop of attacking, deploying, and collecting.

Note: Ensure images in 'pics/' directory match the game's UI.
"""

from humancursor import SystemCursor
import pyautogui, random, time, keyboard, mouse, json, threading
import numpy as np
import easyocr, sys
from PIL import Image
from PIL import ImageEnhance
from pynput.keyboard import Controller
from coords import coords  # Import the large list from coords.py
import pyscreeze, math
from pynput.mouse import Controller as MouseController

mouse_ctl = MouseController()

# Disable PyAutoGUI failsafe (prevents exception when mouse moves to a corner)
pyautogui.FAILSAFE = False
confidence = 0.75  # Default confidence level for image recognition
tolerance = 5  # Tolerance for position comparisons in pixels

# Initialize a "human-like" cursor
cursor = SystemCursor()

FARM_ACCOUNTS = False
ACCOUNTS = []
current_account_index = 0

ICON_IMAGES = [
    r"pics\darkElixirIcon.png",
    r"pics\elixirIcon.png"
]  # List of icon images to collect in the village

ICON_CONFIDENCE = 0.75  # Confidence for icon detection
END_CONFIDENCE = 0.8  # Confidence for end sequence images

X_MIN, X_MAX = 750, 2000  # X-axis range for random movements
Y_MIN, Y_MAX = 250, 900  # Y-axis range for random movements

TOTAL_RUNTIME = 30  # seconds, runtime for random movements simulation

# Small offset for randomized cursor movement
num = 0.0

# keyboard controller (for replay)
kbd = Controller()

# replay state flags (important to prevent overlap)
replaying = False

# replay tuning
TINY_OFFSET_PIXELS = 2
KEY_DELAY = 0.003
BUSYWAIT_SLEEP = 0.0005

# path to recordings
JSON_PATH = "json/recordings.json"

# -----------------------------
# Helper Functions
# -----------------------------


def load_recordings():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        pass

recordings = load_recordings()

def replay_recording_by_index(index):
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False
    global replaying

    data = load_recordings()
    recs = data["recordings"]

    if index < 0 or index >= 14:
        print("❌ Invalid recording index")
        return

    seq = recs[index]["events"]
    if not seq:
        print("❌ Empty recording")
        return

    replaying = True

    try:
        start = time.perf_counter()
        for e in seq:
            while (time.perf_counter() - start) < e["t"]:
                time.sleep(BUSYWAIT_SLEEP)

            ox = random.randint(-TINY_OFFSET_PIXELS, TINY_OFFSET_PIXELS)
            oy = random.randint(-TINY_OFFSET_PIXELS, TINY_OFFSET_PIXELS)

            if e["type"] == "move":
                pyautogui.moveTo(
                    e["x"] + ox,
                    e["y"] + oy,
                    duration=0
                )

            elif e["type"] == "mouse":
                x, y = e["x"] + ox, e["y"] + oy
                if e["action"] == "down":
                    pyautogui.mouseDown(x=x, y=y, button=e["button"])
                else:
                    pyautogui.mouseUp(x=x, y=y, button=e["button"])

            elif e["type"] == "scroll":
                mouse_ctl.scroll(0, e["dy"])

            elif e["type"] == "key":
                if e["action"] == "down":
                    kbd.press(e["key"])
                else:
                    kbd.release(e["key"])
                time.sleep(KEY_DELAY)

    finally:
        replaying = False

def retryAttackAndThenFindMatchAgain():
    location = None
    while location is None:
        try:
            location = pyautogui.locateOnScreen(r"pics\attack.png", confidence=0.70)
        except:
            time.sleep(.3)

    time.sleep(.5)
    center = pyautogui.center(location)
    x, y = center.x, center.y

    pyautogui.moveTo(x,y)
    pyautogui.click(x,y)

    print("THE PROBLEM SHOULD BE FIXED NOW, WE RECLICKED ATTACK, AND WILL NOW SEARCH FOR FIND MATCH AGAIN")

    time.sleep(.5)

def locateOnScreen(path):
    """
    Locate an image on the screen and return its center coordinates (x, y).

    Args:
        path (str): Filepath to the image to locate.

    Returns:
        tuple: (x, y) center coordinates of the found image.
    """
    location = None
    ct = 0
    while location is None:
        try:
            location = pyautogui.locateOnScreen(path, confidence=0.70)
        except Exception:
            # Sleep briefly if an error occurs and try again
            time.sleep(0.1)
            continue

        if location is None:
            # Image not found yet; wait and retry
            time.sleep(0.1)
            ct += 1
            if ct >= 100 and path == r"pics\findMatch.png":
                retryAttackAndThenFindMatchAgain()
                print("TRYING THE NEW FUNCTION FOR FIXING THE PROBLEM")

    # Once found, get the center position
    center = pyautogui.center(location)
    x, y = center.x, center.y
    return x, y


def doMovements(path=None, coords=None, willClick=True, fast=False):
    # Resolve coordinates
    if coords is not None:
        x, y = coords
    elif path is not None:
        x, y = locateOnScreen(path)
    else:
        raise ValueError("Either 'path' or 'coords' must be provided.")

    offset_x = random.uniform(-2, 2)
    offset_y = random.uniform(-2, 2)

    tx = int(x + offset_x)
    ty = int(y + offset_y)

    screen_w, screen_h = pyautogui.size()
    tx = max(1, min(tx, screen_w - 1))
    ty = max(1, min(ty, screen_h - 1))

    cursor.move_to([tx, ty])

    if willClick:
        if fast:
            # ⚡ FAST MODE: ~4x quicker
            time.sleep(random.uniform(0.02, 0.06))
            pyautogui.click()
            time.sleep(random.uniform(0.02, 0.05))
        else:
            # 🧍 NORMAL HUMAN MODE
            time.sleep(random.uniform(0.11, 0.56))
            pyautogui.click()
            time.sleep(random.uniform(0.07, 0.18))

def locateOnScreen_timeout(path, timeout=6, confidence=0.80):
    """Try to locate an image on screen but give up after `timeout` seconds.

    Returns (x, y) center coordinates if found, otherwise returns None.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            loc = pyautogui.locateOnScreen(path, confidence=confidence)
        except Exception as e:
            loc = None

        if loc is not None:
            center = pyautogui.center(loc)
            return center.x, center.y

        time.sleep(0.2)

    return None

# -----------------------------
# Game Action Functions
# -----------------------------

def detectIfLost():
    """
    Checks if the battle is lost by detecting the 'Return Home' button.
    After ~25 seconds (random chance) and again after ~75 seconds (forced),
    attempts to surrender safely by waiting for either surrenderOkay OR returnhome.
    """
    start_time = time.time()
    first_checked = False
    second_checked = False
    needToClickReturnHome = False

    while True:
        elapsed = time.time() - start_time

        # ------------------------------------------------
        # First surrender attempt (25s, 15% chance)
        # ------------------------------------------------
        if not first_checked and elapsed >= 25:
            first_checked = True

            if random.random() <= 0.15:
                x = random.randint(233, 358)
                y = random.randint(1065, 1095)
                print(f"Attempting early surrender after 25 seconds")

                doMovements(coords=(x,y))
                time.sleep(random.uniform(1.0, 1.5))

                result, loc = wait_for_surrender_or_return(timeout=5)

                if loc:
                    cx, cy = pyautogui.center(loc)
                    if result == "surrender":
                        print("Clicking surrender okay")
                        doMovements(coords=(cx,cy))
                        needToClickReturnHome = True
                    elif result == "returnhome":
                        print("Clicking return home")
                        doMovements(coords=(cx,cy))

                    time.sleep(random.uniform(0.5, 1.5))

                    if needToClickReturnHome:
                        print("Clicking return home after surrendering")
                        doMovements(r"pics\returnHome.png")

                    time.sleep(random.uniform(0.5, 1.5))
                    return

        # ------------------------------------------------
        # Second surrender attempt (69s, forced)
        # ------------------------------------------------
        if not second_checked and elapsed >= 69:
            needToClickReturnHome = False
            second_checked = True

            x = random.randint(233, 358)
            y = random.randint(1065, 1095)
            print(f"Attempting forced surrender after 69 seconds")

            doMovements(coords=(x,y))
            time.sleep(random.uniform(1.0, 1.5))

            result, loc = wait_for_surrender_or_return(timeout=5)

            if loc:
                cx, cy = pyautogui.center(loc)
                if result == "surrender":
                    print("Clicking surrender okay")
                    doMovements(coords=(cx,cy))
                    needToClickReturnHome = True
                elif result == "returnhome":
                    print("Clicking return home")
                    doMovements(coords=(cx,cy))
                else:
                    print('we are getting a non None value, but its neither surrender okay or return home. ERROR')

                time.sleep(random.uniform(0.5, 1.5))

                if needToClickReturnHome:
                    print("Clicking return home after surrendering")
                    doMovements(r"pics\returnHome.png")

                time.sleep(random.uniform(0.5, 1.5))
                return
            else:
                print('after 69 seconds, cannot see either surrender okay or return home button')
                return

        # ------------------------------------------------
        # Always check for Return Home
        # ------------------------------------------------
        try:
            rh = pyautogui.locateOnScreen(r"pics/returnHome.png", confidence=0.63)
        except:
            rh = None

        if rh:
            print("Clicking return home after battle end")
            doMovements(r"pics/returnHome.png", willClick=False)
            time.sleep(0.5)
            pyautogui.click()
            return

        time.sleep(0.1)

def wait_for_surrender_or_return(timeout=5):
    """
    Waits for either surrender confirmation or return home.
    Returns ("surrender", location) or ("returnhome", location) or (None, None).
    """
    end_time = time.time() + timeout
    ok = None
    rh = None

    while time.time() < end_time:
        try:
            ok = pyautogui.locateOnScreen(r"pics/surrenderOkay.png", confidence=0.63)
        except:
            ok = None

        if ok:
            return "surrender", ok

        try:
            rh = pyautogui.locateOnScreen(r"pics/returnhome.png", confidence=0.63)
        except:
            rh = None

        if rh:
            return "returnhome", rh

        time.sleep(0.1)
        #print(f'dont see anything: okay:{ok}, returnhome:{rh}')

    return None, None

def clickFindMatch():
    """Clicks the 'Find Match' button on the screen."""
    doMovements(r"pics\findMatch.png")

def clickAttack():
    """Clicks the first 'Attack' button on the screen."""
    doMovements(r"pics\attack.png")

def clickAttack2():
    """Clicks the second 'Attack' button on the screen."""
    doMovements(r"pics\attack2.png")

def findEDragonPicture():
    """Clicks the 'E-Dragon' picture on the screen if found."""
    print("==ATTEMPTING TO FIND THE E-DRAGON PICTURE==")
    doMovements(r"pics\EDragon.png")

def checkIfStarBonus():
    """
    Checks if a star bonus is available and collects it if present.
    Waits briefly before performing the check.
    """
    time.sleep(random.uniform(4.0, 6.0))
    try:
        location = pyautogui.locateOnScreen(r"pics\okay.png", confidence=0.70)
        if location is not None:
            print("Star bonus found, collecting")
            doMovements(r"pics\okay.png")
        else:
            print("DID NOT FIND STAR BONUS")
    except:
        print("DID NOT FIND STAR BONUS")
        pass

def positionAndDeploy():
    global recordings
    if not recordings:
        print("❌ No deploy recordings available")
        return

    chosen_index = random.randint(0,13)
    print(f"==Deploying via human replay #{chosen_index}==")

    replay_recording_by_index(chosen_index)

    time.sleep(1)

def checkLootTotal():
    """
    Screenshots the gold and elixir amounts, reads them using OCR, 
    and decides whether to continue or move to the next match.
    """
    reader = easyocr.Reader(['en'])
    location = None
    ct = 0
    
    while True:
        while location is None:
            try:
                location = pyautogui.locateOnScreen(r"pics\next.png", confidence=.7)
                time.sleep(random.uniform(1, 1.5))
            except:
                if ct < 8:
                    print("DID NOT FIND THE NEXT BUTTON")
                ct  += 1

        time.sleep(.5)
        # Take screenshots of gold and elixir areas
        goldScreenshot = pyautogui.screenshot(region=(261, 194, 179, 35))
        elixirScreenshot = pyautogui.screenshot(region=(256, 257, 178, 31))

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

        print(f"Detected loot amounts: Gold={goldAmount}, Elixir={elixirAmount}")

        totalLoot = goldAmount + elixirAmount

        # If loot is below threshold, click 'Next'
        if totalLoot < 1000000:
            print(f"Loot below threshold ({totalLoot}), searching for next match")
            # This will continuously search until next.png is found
            x, y = locateOnScreen(r"pics\next.png")

            # click it once found
            print("Clicking the next button")
            doMovements(coords=(x,y))  
            time.sleep(random.uniform(4.0, 5.1))
        else:
            # Enough loot collected; stop looping
            print(f"Enough loot: ({totalLoot}), will attack")
            time.sleep(random.uniform(3.00, 4.10))
            break
        
def is_new_position(pos, existing, tol=tolerance):
    """
    Checks if a position is new compared to a list of existing positions, within a tolerance.

    Args:
        pos (tuple): (x, y) position to check.
        existing (list): List of (x, y) tuples of existing positions.
        tol (int): Tolerance in pixels for position comparison.

    Returns:
        bool: True if the position is new, False if it matches an existing one within tolerance.
    """
    for e in existing:
        if abs(pos[0] - e[0]) <= tol and abs(pos[1] - e[1]) <= tol:
            return False
    return True

def safe_locate_all(image_path, confidence=0.75):
    """
    Safely locates all instances of an image on the screen.

    Returns a list of locations or an empty list if not found.

    Args:
        image_path (str): Path to the image file.
        confidence (float): Confidence level for matching.

    Returns:
        list: List of location objects.
    """
    try:
        locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
        return locations
    except pyscreeze.ImageNotFoundException:
        return []
def lightningStrikes():
    """
    Casts lightning strikes on air defense structures in the game.

    Zooms out the map, locates air defense images, and clicks on them multiple times
    based on their level to destroy them with lightning spells.
    """
    print("Centering screen for zoom out")
    doMovements(coords=(1303,713), willClick=False)   #move to center of screen so it zooms out correctly

    # Zoom out completely to ensure proper placement
    print("Zooming out the map for full view")
    for _ in range(random.randint(15, 25)):
        mouse.wheel(random.choice([-5, -4, -6]))
        time.sleep(random.uniform(0.05, 0.3))

    ad_clicks_needed = {
        "AD7.png": 2,
        "AD8.png": 3,
        "AD9.png": 3,
        "AD10.png": 3,
        "AD11.png": 3,
        "AD12.png": 3
    }

    images_to_find = [
        r"pics\AD7.png",
        r"pics\AD8.png",
        r"pics\AD9.png",
        r"pics\AD10.png",
        r"pics\AD11.png",
        r"pics\AD12.png"
    ]

    clicked_positions = []

    # Press the key to select Lightning spell
    print("Selecting lightning spell for casting")
    keyboard.press_and_release('a')
    time.sleep(random.uniform(0.19, 0.3))

    for image_path in images_to_find:
        all_locations = safe_locate_all(image_path, confidence)

        if not all_locations:
            continue

        for loc in all_locations:
            center = pyautogui.center(loc)
            pos = (center.x, center.y)

            if is_new_position(pos, clicked_positions):
                clicked_positions.append(pos)
                image_name = image_path.split("\\")[-1]
                print(f"Found new air defense at position {pos}")

                # Determine how many clicks needed for this Air Defense
                clicks_needed = ad_clicks_needed.get(image_name, 3)

                # Move once near the Air Defense with a small random offset
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)
                click_pos = (pos[0] + offset_x, pos[1] + offset_y)

                # Fast human-like move, no click
                doMovements(coords=click_pos, willClick=False, fast=True)

                # Then fire rapidly at that spot
                for _ in range(clicks_needed):
                    pyautogui.click()
                    time.sleep(random.uniform(0.22, 0.5))

def find_with_scroll(image_path, max_attempts=20, scroll_amount=-5, pause_between=0.1, confidence=0.85):
    """
    Scrolls repeatedly and tries to locate the given image after each scroll step.
    Returns the location if found, or None if not found after max_attempts.

    Params:
      image_path (str): path to the image to locate.
      max_attempts (int): maximum number of scroll-and-try iterations.
      scroll_amount (int): amount of wheel scroll each iteration (negative => down).
      pause_between (float): seconds to wait after scrolling before locating.q
      confidence (float): confidence threshold for image lookup.
    """
    for attempt in range(max_attempts):
        # do a small scroll
        mouse.wheel(scroll_amount)

        # wait a bit for screen to update
        time.sleep(pause_between)

        time.sleep(random.uniform(4.0, 5.0))

        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except:
            continue

        if location is not None:
            return location

    return None

def rgb_to_hex(rgb):
    """Convert (R, G, B) → 'rrggbb' HEX string."""
    return '{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def check_colors(bothFound=False, forWalls=False, whichOne=1):
    targetStorages = [
        ((2130, 120), ["cba90b", "e7c00d"]),
        ((2130, 224), ["c027c0", "a922a9"])
    ]

    goldNumber = [
        ((1475, 1044), "e07770"), #BUG HERE, IF LESS THAN 10 WALLS, THE COORDINATES SHOULD BE THE 1373 ONE, THE RED
        ((1468, 1037), "e07770"), #NUMBER WILL BE IN A DIFFERENT POSITION
        ((1373, 1048), "ff887f")
    ]
    elixirNumber = [
        ((1666, 1040), "e07770"),
        ((1659, 1039), "e07770"),
        ((1565, 1047), "ff887f")
    ]
    redNumberFound = False
    
    bothFound = False

    if not forWalls:
        match_count = 0
        required_matches = 2  # out of the 4 coordinate-hex pairs

        for (x, y), valid_hexes in targetStorages:
            pixel = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
            pixel_hex = rgb_to_hex(pixel).lower()

            # check if the current pixel matches any of its valid hex values
            if pixel_hex in valid_hexes:
                match_count += 1

        if match_count >= required_matches:
            bothFound = True
            return bothFound
    else:
        redNumberFound = False

        if whichOne == 1:
            # GOLD
            for (x, y), _ in goldNumber:
                found = scan_area_for_red(x, y)

                print(f"Checking GOLD near ({x}, {y}) → {'NOT RED' if found else 'RED FOUND'}")

                if found:
                    redNumberFound = True
                    break

        else:
            # ELIXIR
            for (x, y), _ in elixirNumber:
                found = scan_area_for_red(x, y)

                print(f"Checking ELIXIR near ({x}, {y}) → {'NOT RED' if found else 'RED FOUND'}")

                if found:
                    redNumberFound = True
                    break

        return redNumberFound
        
def is_redish(rgb):
    """
    Determines if an RGB color is reddish.

    Args:
        rgb (tuple): (r, g, b) values.

    Returns:
        bool: True if the color is considered red.
    """
    r, g, b = rgb
    return r > 200 and g < 150 and b < 150


def scan_area_for_red(x, y, size=6):
    """
    Scans a square area around (x, y) for reddish pixels.

    Args:
        x (int): Center x coordinate.
        y (int): Center y coordinate.
        size (int): Half-size of the square area.

    Returns:
        bool: True if any reddish pixel is found.
    """
    img = pyautogui.screenshot(region=(x - size, y - size, size * 2, size * 2))
    pixels = img.load()

    for i in range(img.width):
        for j in range(img.height):
            if is_redish(pixels[i, j]):
                return True
    return False

def scan_area_for_hex(x, y, target_hex, size=6):
    """
    Scans a square area around (x, y) for a specific hex color.

    Args:
        x (int): Center x coordinate.
        y (int): Center y coordinate.
        target_hex (str): Hex color string to search for.
        size (int): Half-size of the square area.

    Returns:
        bool: True if the target hex color is found.
    """
    img = pyautogui.screenshot(region=(x - size, y - size, size * 2, size * 2))
    pixels = img.load()

    target_hex = target_hex.lower()

    for i in range(img.width):
        for j in range(img.height):
            pixel_hex = rgb_to_hex(pixels[i, j]).lower()
            if pixel_hex == target_hex:
                return True
    return False

def findWordWallsWithScrolling():
    scroll_image = r"pics\wallWord.png"
    loc = find_with_scroll(
        scroll_image,
        max_attempts=30,
        scroll_amount=-5,
        pause_between=0.15,
        confidence=0.9
    )

    if loc:
        print("Found wallWord.png, moving to click now")
        center = pyautogui.center(loc)
        doMovements(coords=(center.x, center.y))
        return True
    else:
        print("❌ 'Walls' not found after scrolling — assuming none left.")
        return False

def checkIfMaxLoot():
    clicks = 10
    bothFound = False 
    redNumberFound = False
    onlyOneWall = False
    time.sleep(random.uniform(5.0, 6.0))

    bothFound = check_colors(forWalls=False)

    if not bothFound:
        print('Storages are not full')
        return False

    print("📦 Storages full detected.")

    # -----------------------------------
    # CASE 1: Stop on full, but farm others
    # -----------------------------------
    if STOP_ON_FULL_STORAGES and FARM_ACCOUNTS:
        print("Storages full, switching to next account")
        switch_to_next_account()
        return True

    # -----------------------------------
    # CASE 2: Stop on full, no other accounts
    # -----------------------------------
    if STOP_ON_FULL_STORAGES and not FARM_ACCOUNTS:
        print("Storages full, stopping the bot")
        sys.exit(0)

    # -----------------------------------
    # CASE 3: Upgrade walls until none left
    # -----------------------------------
    print("Starting wall upgrade process")

    print("Searching for builder face")

    doMovements(r"pics\builderFace.png")
    print("Builder face found")

    time.sleep(random.uniform(0.19, 0.3))

    doMovements(coords=(1351,512), willClick=False)        
    print("Navigating to builder menu position")
    time.sleep(random.uniform(0.19, 0.3))

    print("==TRYING TO FIND WORD WITH SCROLLING (PART 1)==")
    didWeFindWordWalls = findWordWallsWithScrolling()  

    time.sleep(random.uniform(1.00, 2.00))

    print("Checking if there is only one wall")
    try:
        redUpgrade = pyautogui.locateOnScreen(r"pics\redUpgrade.png", confidence=0.95)
        if redUpgrade is not None:
            onlyOneWall = True
    except:
        pass

    if not onlyOneWall:
        print("Multiple walls available")
        time.sleep(random.uniform(0.3, 0.45))
        print("Attempting to click the 'Upgrade More' button")
        doMovements(r"pics\upgradeMore.png")

        time.sleep(random.uniform(2.0, 3.45))
        
        searchFor10LocationAndReact()

        for _ in range(clicks):
            print("Attempting wall upgrade click")
            pyautogui.click()
            time.sleep(random.uniform(0.5, 1.0))
            redNumberFound = check_colors(forWalls=True)
            if redNumberFound:
                print("Red number detected, removing 1 wall to fix")
                doMovements(r"pics\remove.png")
                time.sleep(random.uniform(1.00, 1.45))
                break
            time.sleep(random.uniform(0.19, 0.3))

        print("Attempting to click upgrade")
        doMovements(r"pics\upgrade.png")
        print("Attempting to click the okayWalls.png")
        doMovements(r"pics\okayWalls.png") 
        print("Attempting to click the builder face")
        doMovements(r"pics\builderFace.png")

        time.sleep(random.uniform(0.19, 0.3))
        print("Moving cursor in position to start scrolling")
        doMovements(coords=(1351,512), willClick=False)  
        time.sleep(random.uniform(0.19, 0.3))

        print("==TRYING TO FIND WORD WITH SCROLLING PART 2==")
        didWeFindWordWalls = findWordWallsWithScrolling()

        print("Clicking 'Upgrade More' again")
        doMovements(r"pics\upgradeMore.png")

        searchFor10LocationAndReact()

        time.sleep(random.uniform(2.0, 3.0))

        for _ in range(clicks):
            print("Attempting second wall upgrade click")
            pyautogui.click()
            time.sleep(random.uniform(0.5, 0.65))
            redNumberFound = check_colors(forWalls=True, whichOne=2)
            if redNumberFound:
                print("Red number detected for elixir number, removing 1 wall")
                doMovements(r"pics\remove.png")
                time.sleep(random.uniform(1.00, 1.78))
                break
            time.sleep(random.uniform(0.19, 0.3))

        print("Clicking upgrade")
        upgrade_x, upgrade_y = locateOnScreen(r"pics\upgrade.png")
        doMovements(coords=(upgrade_x+200,upgrade_y))  
        print("Clicking okayWalls.png again")
        doMovements(r"pics\okayWalls.png")
    else:
        print("Only one wall available, upgrading single wall")
        upgrade_x, upgrade_y = locateOnScreen(r"pics\upgrade.png")
        print("Adjusting cursor for single upgrade")
        doMovements(coords=(upgrade_x+200,upgrade_y))  
        time.sleep(random.uniform(1.0, 1.5))
        print("Confirming single wall upgrade")
        doMovements(r"pics\confirm.png")
        time.sleep(random.uniform(0.5, 1.0))

        # small pause before trying next wall
        time.sleep(random.uniform(1.5, 3.0))

    # -----------------------------------
    # After all walls are done
    # -----------------------------------
    if FARM_ACCOUNTS and not didWeFindWordWalls:
        print("Wall upgrades completed. Program stopping")
        switch_to_next_account()
        return True
    
    print("Used all resources to upgrade walls")


def searchFor10LocationAndReact():
    tenLocation = None

    try:
        tenLocation = pyautogui.locateOnScreen(r"pics\10.png", confidence=.98)
        print("Searching for '10' indicator which tells us where to move the cursor")
    except Exception as e:
        tenLocation = None

    if tenLocation is not None:
        ten_x, ten_y = pyautogui.center(tenLocation)
        print("Moving to the button to the right of 10.png")
        doMovements(coords=(ten_x+200,ten_y), willClick=False)  
    else:
        addWall = locateOnScreen_timeout(r"pics\addWall.png", timeout=6, confidence=0.95)
        if addWall is None:
            print("upgrade button not found; skipping upgrades")
        else:
            addWall_x, addWall_y = addWall
            print("Moving to addWall.png")
            doMovements(coords=(addWall_x,addWall_y), willClick=False)

def checkIfOutOfGold():
    #IF WE DETECT WE HAVE NO GOLD, QUICKLY COLLECT SOME FROM THE COLLECTORS AND RE SEARCH FOR AN ATTACK
    time.sleep(random.uniform(.5, 1))
    try:
        location = pyautogui.locateOnScreen(r"pics\youNeedMoreGoldX.png", confidence=0.80)
        if location is not None:
            print("Gold depleted, collecting from collectors and retrying attack")
            print("Closing insufficient gold prompt")
            doMovements(r"pics\youNeedMoreGoldX.png")
            print("Zooming out to locate gold collectors")
            for _ in range(random.randint(15, 25)):
                mouse.wheel(random.choice([-5, -4, -6]))
                time.sleep(random.uniform(0.05, 0.3))
            print("Clicking gold collector icon")
            doMovements(r"pics\goldCollectorIcon.png")
            clickAttack()
            clickFindMatch()
            clickAttack2()
    except:
        print("We have enough gold, proceding now")
        pass

def switch_to_next_account():
    global current_account_index

    if current_account_index >= len(ACCOUNTS):
        print("All accounts processed, stopping bot")
        sys.exit(0)

    name = ACCOUNTS[current_account_index]
    print(f"Switching to account: {name}")

    print("Opening settings menu")
    doMovements(r"pics\settings.png")
    time.sleep(random.uniform(0.8, 1.3))

    print("Clicking switch account button")
    doMovements(r"pics\switchAccountButton.png")
    time.sleep(random.uniform(0.8, 1.3))

    print(f"Selecting account {name}")
    doMovements(rf"pics\{name}.png")
    print("Waiting for account switch to complete")
    time.sleep(random.uniform(10, 12))

    try:
        loc = pyautogui.locateOnScreen(r"pics\okayFromReloading.png", confidence=0.8)
        if loc:
            print("Clicking ok from reloading")
            doMovements(r"pics\okayFromReloading.png")
    except:
        print("DID NOT FIND OKAY FROM RELOADING")

    current_account_index += 1
    
# -----------------------------
# HELPERS
# -----------------------------

def human_pause(a=0.1, b=0.5):
    """
    Pauses execution for a random duration between a and b seconds to simulate human timing.

    Args:
        a (float): Minimum pause time.
        b (float): Maximum pause time.
    """
    pause_time = random.uniform(a, b)
    time.sleep(pause_time)

def move_human(x, y):
    """
    Moves the cursor to the specified coordinates using the human-like cursor.

    Args:
        x (int): X coordinate.
        y (int): Y coordinate.
    """
    cursor.move_to([x, y])

def random_point():
    """
    Generates a random point within the defined screen bounds.

    Returns:
        tuple: (x, y) random coordinates.
    """
    point = random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX)
    return point

def small_drag():
    """
    Performs a small random drag operation to simulate human interaction.
    """
    dx = random.randint(-80, 80)
    dy = random.randint(-80, 80)

    pyautogui.mouseDown()
    cur = pyautogui.position()
    cursor.move_to([cur.x + dx, cur.y + dy])
    pyautogui.mouseUp()

def maybe_click():
    """
    Randomly performs a click with a 35% chance to simulate occasional human clicks.
    """
    if random.random() < 0.35:
        human_pause(0.05, 0.2)
        pyautogui.click()

def maybe_zoom():
    """
    Randomly performs zoom operations with a 40% chance to simulate human zooming.
    """
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

    move_human(cx, cy)
    human_pause(0.2, 0.4)

    for _ in range(random.randint(12, 18)):
        pyautogui.scroll(-300)
        human_pause(0.05, 0.12)

# -----------------------------
# ICON COLLECTION
# -----------------------------

def collect_icons():
    """
    Collects resources from icons in the village by locating and clicking them.
    """
    for icon in ICON_IMAGES:
        print(f"Attempting to collect {icon}")
        try:
            loc = pyautogui.locateOnScreen(icon, confidence=ICON_CONFIDENCE)
        except Exception:
            loc = None

        if loc:
            c = pyautogui.center(loc)
            move_human(c.x, c.y)
            human_pause(0.1, 0.3)
            pyautogui.click()
            human_pause(0.3, 0.6)
        else:
            print(f"{icon} not found")

# -----------------------------
# END SEQUENCE (20% chance)
# -----------------------------

def end_sequence():
    # Step 1: random click in given range
    print("Clicking the level button at the top left")
    x = random.randint(230, 266)
    y = random.randint(93, 123)
    move_human(x, y)
    human_pause(0.1, 0.3)
    pyautogui.click()

    time.sleep(1.0)

    # Step 2: find myClan.png
    print("Searching for My Clan button")
    try:
        loc = pyautogui.locateOnScreen(r"pics\myClan.png", confidence=END_CONFIDENCE)
    except Exception:
        loc = None

    if loc:
        print("Clicking My Clan button")
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
    print("Searching for close button")
    try:
        loc_x = pyautogui.locateOnScreen(r"pics\x.png", confidence=END_CONFIDENCE)
    except Exception:
        loc_x = None

    if loc_x:
        print("Clicking close button")
        c2 = pyautogui.center(loc_x)
        move_human(c2.x, c2.y)
        human_pause(0.1, 0.3)
        pyautogui.click()
    
def doRandomMovementsInVillage():
    alreadyDidSomething = False
    randomMovements = False
    time.sleep(3)

    # has a 5% chance to wait for the game to timeout, and auto reload it to look like a human break
    if random.random() < 0.005:
        print('Waiting for game to timeout .5 percent chance to happen')
        print("Will attempt to find the reload game button soon")
        doMovements(r"pics\reloadGame.png")
        pyautogui.click()
        print("Waiting for game to reload")
        time.sleep(11)
        try:
            location = pyautogui.locateOnScreen(r"pics\okayFromReloading.png", confidence=0.70)
            if location is not None:
                print("Confirming game reload")
                doMovements(r"pics\okayFromReloadin.png")
        except:
            print("DID NOT FIND THE OKAY FROM RELOADING AFTER GAME TIMEOUT")
        time.sleep(3)
        alreadyDidSomething = True

    # has a chance of not doing anything for 10-32 seconds
    if random.random() < 0.15 and not alreadyDidSomething:
        print("Taking a short break for human simulation")
        time.sleep(random.uniform(10,32))
        alreadyDidSomething = True

    # 95% chance to NOT run
    if random.random() > 0.05 and not alreadyDidSomething:
        return
    else:
        randomMovements = True

    if randomMovements and not alreadyDidSomething:
        print("==STARTING RANDOM MOVEMENTS IN VILLAGE (5% chance)==")

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
            alreadyDidSomething = True

    # 13% chance to run end sequence
    if random.random() < 0.13 and not alreadyDidSomething:
        print("Running end sequence (13% chance)")
        end_sequence()
    else:
        print("Skipping end sequence (87% chance).")
    time.sleep(1.5)

def doTestModeSequence():
    print("==TEST MODE: QUICK ATTACK==")

    clickAttack()
    clickFindMatch()
    clickAttack2()

    print("==POSITION AND DEPLOY TROOPS==")
    time.sleep(3)
    positionAndDeploy()    

def point_in_polygon(x, y, polygon):
    inside = False
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        if ((y1 > y) != (y2 > y)) and \
           (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside

    return inside

def is_near_existing(x, y, points, radius):
    for fx, fy in points:
        if (x - fx) ** 2 + (y - fy) ** 2 <= radius ** 2:
            return True
    return False

def scan_for_images(images, diamond, confidence, radius):
    found_points = []

    for img in images:
        try:
            matches = list(pyautogui.locateAllOnScreen(
                f"pics/{img}",
                confidence=confidence
            ))
        except:
            continue

        for match in matches:
            center = pyautogui.center(match)

            if not point_in_polygon(center.x, center.y, diamond):
                continue

            if is_near_existing(center.x, center.y, found_points, radius):
                continue

            found_points.append((center.x, center.y))

    return found_points

def click_points(points):
    time.sleep(.2)
    for x, y in points:
        pyautogui.moveTo(x,y)
        pyautogui.click(x,y)
        time.sleep(1)

        pyautogui.moveTo(1322,1133) #hard coords for remove button
        pyautogui.click(1322,1133)
        time.sleep(.8)


def clean_the_base():
    images = [
        "tree.png",
        "bush.png",
        "big_tree.png",
        "wood.png",
        "emerald_box.png",
        "flower_bed.png",
        "log.png"
    ]

    #this diamond is the base diamond shape
    diamond = [(1297,55), (2280,727), (1282,1358), (290,733)]

    confidence = 0.8
    radius = 6

    time.sleep(1.2)
    points = scan_for_images(images, diamond, confidence, radius)

    if not points:
        return

    click_points(points) 

# -----------------------------
# Main Loop
# -----------------------------

#DONT DO ANY EXTRA SHIT, ONLY FOR TESTING
TEST_MODE = False

def main():
    global TEST_MODE
    global CLEAN_THE_BASE

    #activate the coc window
    pyautogui.moveTo(1326,30)
    pyautogui.click(1326,30)

    if CLEAN_THE_BASE:
        print("==CLEANING THE BASE FIRST==")
        clean_the_base()

    while True:
        if not TEST_MODE:
            print("\n\n\n=======NEW ITERATION=======")
            print("==CHECKING FOR STAR BONUS==")
            checkIfStarBonus()

            print("==CHECKING IF STORAGES ARE FULL==")
            switched = checkIfMaxLoot()
            if switched:
                print("Account switched, restarting automation cycle")
                continue  # restart loop after account switch

            doRandomMovementsInVillage()
            print("==ATTEMPTING TO CLICK ATTACK==")
            clickAttack() 
            print("==ATTEMPTING TO CLICK NEW MATCH==")
            clickFindMatch() 
            print("==ATTEMPTING TO CLICK ATTACK 2 BUTTON==")
            clickAttack2() 
            print("==CHECKING IF WE ARE OUT OF GOLD==")
            checkIfOutOfGold()
            print("==CHECKING ENEMY LOOT TOTAL==")
            checkLootTotal() 
            print("==POSITION AND DEPLOY TROOPS==")
            positionAndDeploy() 
            print("==MONITORING BATTLE FOR LOSS==")
            detectIfLost()
        else:
            doTestModeSequence()

if not TEST_MODE:
    print("Farm resources on other accounts?")
    print("Enter names: gavbl, dave, dark. Type 'q' when done.")

    while True:
        name = input("Account name (or q): ").strip().lower()
        if name == "q":
            break
        if name in ["gavbl", "dave", "dark"]:
            ACCOUNTS.append(name)
        else:
            print("Invalid name. Use: gavbl, dave, dark.")

    if ACCOUNTS:
        FARM_ACCOUNTS = True
        print("Accounts to farm:", ACCOUNTS)
    else:
        FARM_ACCOUNTS = False
        print("No extra accounts selected.")
            
    # Prompt user for configuration
    STOP_ON_FULL_STORAGES = None
    CLEAN_THE_BASE = None

    while STOP_ON_FULL_STORAGES is None:
        user_input = input("Stop program when storages are full? (y/n): ").strip().lower()
        if user_input == "y":
            STOP_ON_FULL_STORAGES = True
        elif user_input == "n":
            STOP_ON_FULL_STORAGES = False

    while CLEAN_THE_BASE is None:
        user_input = input("Do you want to clean the base? (y/n): ").strip().lower()
        if user_input == "y":
            CLEAN_THE_BASE = True
        elif user_input == "n":
            CLEAN_THE_BASE = False

# Start the main automation loop
print("Initialization complete, starting main automation loop")
main()
