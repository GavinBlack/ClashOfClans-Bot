import pyautogui
import pyscreeze
import time
import random, keyboard

pyautogui.FAILSAFE = False
confidence = 0.75
tolerance = 5

time.sleep(2)

images_to_find = [
    r"pics\AD7.png",
    r"pics\AD8.png",
    r"pics\AD9.png",
    r"pics\AD10.png",
    r"pics\AD11.png"
]

# Map Air Defense image to number of lightning clicks needed
ad_clicks_needed = {
    "AD7.png": 2,
    "AD8.png": 3,
    "AD9.png": 3,
    "AD10.png": 3,
    "AD11.png": 3
}

clicked_positions = []

# -----------------------------
# Helper Functions
# -----------------------------
def is_new_position(pos, existing, tol=tolerance):
    for e in existing:
        if abs(pos[0] - e[0]) <= tol and abs(pos[1] - e[1]) <= tol:
            return False
    return True

def safe_locate_all(image_path, confidence=0.75):
    try:
        return list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
    except pyscreeze.ImageNotFoundException:
        return []

# -----------------------------
# Main Function
# -----------------------------
def main():
    while True:
        # Press the key to select Lightning spell
        keyboard.press_and_release('a')
        time.sleep(0.2)

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
                    print(f"Found {image_name} at {pos}")

                    # Determine how many clicks needed for this Air Defense
                    clicks_needed = ad_clicks_needed.get(image_name, 3)

                    for _ in range(clicks_needed):
                        # Add small human-like random offset
                        offset_x = random.randint(-3, 3)
                        offset_y = random.randint(-3, 3)
                        click_pos = (pos[0] + offset_x, pos[1] + offset_y)

                        pyautogui.moveTo(click_pos, duration=random.uniform(0.1, 0.3))
                        pyautogui.click()
                        time.sleep(random.uniform(0.05, 0.15))

        break  # run once; remove to loop continuously

if __name__ == "__main__":
    main()
