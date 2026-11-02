import cv2
import numpy as np

from guidestride.lane_detection import LaneDetector


def synthetic_frame(shift: int = 0) -> np.ndarray:
    h, w = 540, 960
    frame = np.full((h, w, 3), 40, dtype=np.uint8)
    y_top = int(h * 0.55)
    cx = w // 2 + shift
    cv2.line(frame, (cx - 280, h - 1), (cx - 75, y_top), (255, 255, 255), 8)
    cv2.line(frame, (cx + 280, h - 1), (cx + 75, y_top), (255, 255, 255), 8)
    return frame


def test_detects_two_boundaries_and_center() -> None:
    result = LaneDetector(smoothing_alpha=1.0).detect(synthetic_frame())
    assert result.left_line is not None
    assert result.right_line is not None
    assert result.lane_center_x is not None
    assert abs(result.normalized_offset or 0.0) < 0.08
    assert result.confidence > 0.4


def test_offset_sign_matches_runner_position() -> None:
    detector = LaneDetector(smoothing_alpha=1.0)
    right_shifted_lane = detector.detect(synthetic_frame(shift=70))
    assert right_shifted_lane.normalized_offset is not None
    assert right_shifted_lane.normalized_offset < 0
