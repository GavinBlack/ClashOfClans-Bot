import pyautogui
import cv2
import numpy as np

# -----------------------------
# Config
# -----------------------------

X1, Y1 = 663, 134
X2, Y2 = 1973, 1076
W, H = X2 - X1, Y2 - Y1

TARGET_HEX = "#ff5dff"
MAX_BLOBS = 4
MIN_AREA = 200

OUTPUT_FILE = "ff5dff_blob_debug.png"

# -----------------------------
# Build HSV range from hex
# -----------------------------

target_rgb = np.uint8([[[255, 93, 255]]])  # ff5dff
target_hsv = cv2.cvtColor(target_rgb, cv2.COLOR_RGB2HSV)[0][0]
h, s, v = int(target_hsv[0]), int(target_hsv[1]), int(target_hsv[2])

H_TOL = 8
S_MIN = max(0, s - 60)
V_MIN = max(0, v - 60)

LOWER = np.array([max(0, h - H_TOL), S_MIN, V_MIN])
UPPER = np.array([min(179, h + H_TOL), 255, 255])

print("Target HSV:", (h, s, v))
print("HSV range:", LOWER, UPPER)

# -----------------------------
# Main detection function
# -----------------------------

def detect_elixir_blobs():
    screenshot = pyautogui.screenshot(region=(X1, Y1, W, H))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER, UPPER)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blobs = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= MIN_AREA:
            (x, y), r = cv2.minEnclosingCircle(cnt)
            blobs.append((int(x), int(y), int(r), int(area)))

    print(f"Total candidate blobs found: {len(blobs)}")

    blobs.sort(key=lambda b: b[3], reverse=True)
    top_blobs = blobs[:MAX_BLOBS]

    print(f"Using top {len(top_blobs)} biggest blobs")

    output = img.copy()

    if top_blobs:
        for i, (x, y, r, area) in enumerate(top_blobs, 1):
            cv2.circle(output, (x, y), max(r, 15), (0, 255, 0), 2)
            cv2.putText(output, f"{i}", (x - 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        cx, cy = W // 2, H // 2
        cv2.circle(output, (cx, cy), 40, (0, 0, 255), 2)
        cv2.putText(output, "not very sure", (cx - 60, cy - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imwrite(OUTPUT_FILE, output)
    print(f"Saved debug image: {OUTPUT_FILE}")

    return top_blobs

# -----------------------------
# Entry point
# -----------------------------

if __name__ == "__main__":
    blobs = detect_elixir_blobs()
    centers = [(b[0], b[1]) for b in blobs]
    print("Top blob centers (relative to region):", centers)
