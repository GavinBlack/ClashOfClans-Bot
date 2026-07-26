import pyautogui
import time
import math

time.sleep(2)

# Images to search
images = [
    "tree.png",
    "bush.png",
    "big_tree.png",
    "wood.png",
    "emerald_box.png",
    "flower_bed.png",
    "log.png"
]

# Store found points
found_points = []

# -----------------------------
# Diamond (for filtering)
# -----------------------------
diamond = [(1297,55), (2280,727), (1282,1358), (290,733)]

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

# -----------------------------
# Deduplication (15px radius)
# -----------------------------
def is_near_existing(x, y, radius=8):
    for fx, fy in found_points:
        if (x - fx) ** 2 + (y - fy) ** 2 <= radius ** 2:
            return True
    return False

# -----------------------------
# FIND ALL IMAGES
# -----------------------------
for img in images:
    print(f"Scanning for {img}...")

    try:
        matches = list(pyautogui.locateAllOnScreen(
            f"pics/{img}",
            confidence=0.77
        ))
    except:
        continue

    for match in matches:
        center = pyautogui.center(match)

        # Only keep if inside diamond
        if not point_in_polygon(center.x, center.y, diamond):
            continue

        # Skip duplicates
        if is_near_existing(center.x, center.y):
            continue

        print(f"Found {img} at {center}")
        found_points.append((center.x, center.y))

# -----------------------------
# CLICK ALL FOUND POINTS
# -----------------------------

print("\nClicking all found points...\n")
ct = 0
for x, y in found_points:
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(.1)

    pyautogui.moveTo(1322,1133)
    pyautogui.click(1322,1133)
    time.sleep(5)