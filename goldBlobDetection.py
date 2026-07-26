import pyautogui
import cv2
import numpy as np

# -----------------------------
# Config
# -----------------------------

X1, Y1 = 663, 134
X2, Y2 = 1973, 1076
W, H = X2 - X1, Y2 - Y1

# From your measurement: 1313 - 1256 = ~57 px
EXPECTED_DIAMETER = 57
DIAM_TOL = 20   # allow some error

MIN_DIAM = EXPECTED_DIAMETER - DIAM_TOL
MAX_DIAM = EXPECTED_DIAMETER + DIAM_TOL

MAX_RESULTS = 4

EDGE_DEBUG = "gold_edges_debug.png"
OUT_FILE = "gold_square_debug.png"

# -----------------------------
# Detection
# -----------------------------

def detect_gold_squares():
    screenshot = pyautogui.screenshot(region=(X1, Y1, W, H))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Grayscale + blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edges = cv2.Canny(gray, 40, 120)
    cv2.imwrite(EDGE_DEBUG, edges)
    print(f"Saved edges debug: {EDGE_DEBUG}")

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 300:
            continue

        # Fit rotated rectangle
        rect = cv2.minAreaRect(cnt)  # ((cx,cy),(w,h),angle)
        (cx, cy), (rw, rh), angle = rect

        if rw <= 1 or rh <= 1:
            continue

        # Square-ish check
        aspect = max(rw, rh) / min(rw, rh)
        if aspect > 1.3:
            continue

        # Size check against expected diameter
        if not (MIN_DIAM <= rw <= MAX_DIAM and MIN_DIAM <= rh <= MAX_DIAM):
            continue

        box = cv2.boxPoints(rect)
        box = np.int32(box)

        candidates.append({
            "cx": int(cx),
            "cy": int(cy),
            "rw": float(rw),
            "rh": float(rh),
            "angle": float(angle),
            "area": float(area),
            "box": box
        })

    print(f"Square-like candidates found: {len(candidates)}")

    # Pick top 4 by area
    candidates.sort(key=lambda d: d["area"], reverse=True)
    top = candidates[:MAX_RESULTS]

    out = img.copy()

    if top:
        for i, d in enumerate(top, 1):
            cv2.drawContours(out, [d["box"]], 0, (0, 255, 0), 2)
            cv2.circle(out, (d["cx"], d["cy"]), 3, (0, 255, 0), -1)
            cv2.putText(
                out,
                f"{i} {int(d['rw'])}x{int(d['rh'])}",
                (d["cx"] - 40, d["cy"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 0),
                1
            )
    else:
        cv2.circle(out, (W // 2, H // 2), 40, (0, 0, 255), 2)
        cv2.putText(
            out,
            "not very sure",
            (W // 2 - 60, H // 2 - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

    cv2.imwrite(OUT_FILE, out)
    print(f"Saved result: {OUT_FILE}")

    centers = [(d["cx"], d["cy"]) for d in top]
    print("Top centers (relative to region):", centers)

    return top

# -----------------------------
# Entry point
# -----------------------------

if __name__ == "__main__":
    detect_gold_squares()
