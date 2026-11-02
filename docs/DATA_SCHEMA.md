# Data schema

## Raw collection session

A Raspberry Pi collection session is stored under:

```text
dataset/raw/<session_id>/
```

### `video.mp4`

Raw camera stream.

### `frames.csv`

| column | description |
|---|---|
| `frame` | zero-based video frame index |
| `timestamp_s` | monotonic seconds from session start |

### `imu.csv`

| column | description |
|---|---|
| `timestamp_s` | monotonic seconds from session start |
| `ax`, `ay`, `az` | acceleration in g |
| `gx`, `gy`, `gz` | angular velocity in degrees/second |

### `metadata.json`

Stores session ID, UTC creation time, camera settings, requested duration, frame dimensions, whether IMU was enabled, and whether labels/features are included.

## Labeled training table

`train_random_forest.py` expects the following columns:

```text
normalized_offset
smoothed_offset
offset_slope
lane_confidence
ax
ay
az
gx
gy
gz
label
```

Valid label vocabulary:

```text
LEFT_DRIFT
STABLE
RIGHT_DRIFT
```

## Data principle

Raw sensor/video capture is kept separate from derived features and labels. This preserves reproducibility and allows the feature-engineering pipeline to change without destroying the original measurements.
