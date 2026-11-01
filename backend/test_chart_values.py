
import cv2
import numpy as np

IMAGE_PATH = (
    r"data\layout_crops"
    r"\86bc8d6d-d871-4286-b7a0-d24b9da5e655"
    r"\page_1_figure_1.png"
)

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(f"Chart image not found: {IMAGE_PATH}")

height, width = image.shape[:2]

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Isolate blue bars.
mask = cv2.inRange(
    hsv,
    np.array([90, 40, 40]),
    np.array([130, 255, 255]),
)

contours, _ = cv2.findContours(
    mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

bars = []

for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)

    # Exclude the large chart border and tiny regions.
    if w >= 40 and w <= 150 and h >= 50 and cv2.contourArea(contour) > 1000:
        bars.append((x, y, w, h))

bars.sort(key=lambda item: item[0])

if len(bars) != 4:
    raise ValueError(
        f"Expected 4 bars, detected {len(bars)}. "
        f"Bounding boxes: {bars}"
    )

# Approximate plot coordinates based on this test chart.
# These coordinates must be recalibrated for other charts.
plot_top = 16
plot_bottom = 271

axis_max = 100
axis_min = 0

print(f"Image dimensions: {width} x {height}")
print(f"Plot vertical range: {plot_top} to {plot_bottom}")
print()

for index, (x, y, w, h) in enumerate(bars, start=1):
    bar_top = y
    estimated_value = (
        (plot_bottom - bar_top)
        / (plot_bottom - plot_top)
        * (axis_max - axis_min)
        + axis_min
    )

    print(
        f"Bar {index}: "
        f"x={x}, y={y}, width={w}, height={h}, "
        f"estimated_value={estimated_value:.1f}"
    )
