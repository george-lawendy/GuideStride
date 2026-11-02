"""Visualization helpers for the current GuideStride software demo."""

from __future__ import annotations

import cv2
import numpy as np

from .drift import DriftEstimate
from .lane_detection import LaneEstimate


def _draw_line(frame: np.ndarray, line: tuple[int, int, int, int] | None) -> None:
    if line is None:
        return
    x1, y1, x2, y2 = line
    cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 4, cv2.LINE_AA)


def draw_overlay(
    frame: np.ndarray,
    lane: LaneEstimate,
    drift: DriftEstimate,
    fps: float | None = None,
) -> np.ndarray:
    """Render a clean engineering dashboard onto a video frame."""
    output = frame.copy()
    height, width = output.shape[:2]

    _draw_line(output, lane.left_line)
    _draw_line(output, lane.right_line)

    if lane.lane_center_x is not None:
        center_x = int(lane.lane_center_x)
        cv2.line(output, (center_x, int(height * 0.55)), (center_x, height - 1), (255, 255, 255), 2)

    runner_x = int(lane.runner_x)
    cv2.line(output, (runner_x, int(height * 0.70)), (runner_x, height - 1), (200, 200, 200), 2)

    panel_w = min(355, width - 20)
    cv2.rectangle(output, (10, 10), (10 + panel_w, 176), (0, 0, 0), -1)

    offset_text = "n/a" if lane.normalized_offset is None else f"{lane.normalized_offset:+.3f}"
    slope_text = "n/a" if drift.offset_slope is None else f"{drift.offset_slope:+.4f}"
    fps_text = "n/a" if fps is None else f"{fps:.1f}"

    rows = [
        ("GuideStride v0.1", 32),
        (f"Command: {drift.guidance}", 58),
        (f"Drift: {drift.state.value}", 82),
        (f"Center error: {offset_text}", 106),
        (f"Error slope: {slope_text}", 130),
        (f"Lane conf: {lane.confidence:.2f} | FPS: {fps_text}", 154),
    ]

    for text, y in rows:
        cv2.putText(output, text, (22, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    # Virtual haptic indicators. Mapping follows the planned hardware logic:
    # left motor -> move right; right motor -> move left.
    left_active = drift.guidance == "MOVE RIGHT"
    right_active = drift.guidance == "MOVE LEFT"
    y = height - 35
    cv2.putText(output, "L MOTOR", (25, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.circle(output, (125, y - 5), 10, (255, 255, 255), -1 if left_active else 1)
    cv2.putText(output, "R MOTOR", (width - 155, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.circle(output, (width - 30, y - 5), 10, (255, 255, 255), -1 if right_active else 1)

    return output
