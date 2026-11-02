# Architecture

GuideStride is designed as an end-to-end edge perception and feedback system.

## 1. Sensing

- **Forward-facing camera**: path/lane geometry and lateral position.
- **MPU6050 IMU**: 3-axis acceleration and 3-axis angular velocity.

## 2. Perception

The current baseline uses OpenCV:

1. grayscale conversion
2. Gaussian smoothing
3. Canny edge detection
4. trapezoidal region of interest
5. probabilistic Hough transform
6. left/right line grouping
7. median line fitting
8. lane-center estimation
9. exponential temporal smoothing

The previous OpenCV array-shape issue is handled by flattening each Hough-line item before extracting `x1, y1, x2, y2`, making the code tolerant of `(1, 4)` style outputs.

## 3. Feature engineering

Current/planned baseline features:

1. normalized center offset
2. smoothed center offset
3. lateral offset slope
4. lane-detection confidence
5. accelerometer X
6. accelerometer Y
7. accelerometer Z
8. gyroscope X
9. gyroscope Y
10. gyroscope Z

The architecture is intentionally modular so additional temporal or missingness features can be evaluated without rewriting the perception layer.

## 4. Classification

Target classes:

- `LEFT_DRIFT`
- `STABLE`
- `RIGHT_DRIFT`

The current demo uses interpretable threshold-based temporal logic. A Random Forest baseline is prepared for real labeled multimodal data because it is computationally lightweight, handles nonlinear interactions, and provides feature-importance signals useful during early experiments.

## 5. Guidance

Current simulated mapping:

- `LEFT_DRIFT` → **MOVE RIGHT**
- `STABLE` → **CENTERED**
- `RIGHT_DRIFT` → **MOVE LEFT**
- low confidence → **HOLD / LOW CONFIDENCE**

Planned hardware mapping:

- left-side vibration motor → cue runner to move right
- right-side vibration motor → cue runner to move left
- no vibration → centered

## 6. Safety / uncertainty

The system should not output confident directional commands when perception confidence is low. The current baseline therefore produces an `UNKNOWN` state when lane confidence drops below a defined threshold.
