"""OpenCV path/lane detection and lane-center estimation.

This module intentionally keeps the current baseline classical and interpretable.
It is suitable for prerecorded-video validation and for generating features before
moving to more complex learned perception models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import cv2
import numpy as np


@dataclass(frozen=True)
class LaneEstimate:
    """Per-frame lane estimate returned by :class:`LaneDetector`."""

    left_line: tuple[int, int, int, int] | None
    right_line: tuple[int, int, int, int] | None
    lane_center_x: float | None
    runner_x: float
    normalized_offset: float | None
    confidence: float


class LaneDetector:
    """Detect two dominant lane/path boundaries with a Hough-line baseline."""

    def __init__(
        self,
        roi_top_ratio: float = 0.55,
        canny_low: int = 50,
        canny_high: int = 150,
        smoothing_alpha: float = 0.25,
    ) -> None:
        if not 0.0 < roi_top_ratio < 1.0:
            raise ValueError("roi_top_ratio must be between 0 and 1")
        if not 0.0 < smoothing_alpha <= 1.0:
            raise ValueError("smoothing_alpha must be in (0, 1]")

        self.roi_top_ratio = roi_top_ratio
        self.canny_low = canny_low
        self.canny_high = canny_high
        self.smoothing_alpha = smoothing_alpha
        self._smoothed_center: float | None = None

    @staticmethod
    def _line_x_at_y(line: tuple[int, int, int, int], y: int) -> float | None:
        x1, y1, x2, y2 = line
        if y2 == y1:
            return None
        t = (y - y1) / (y2 - y1)
        return x1 + t * (x2 - x1)

    @staticmethod
    def _fit_average_line(
        candidates: Iterable[tuple[float, float]],
        y_bottom: int,
        y_top: int,
    ) -> tuple[int, int, int, int] | None:
        values = list(candidates)
        if not values:
            return None

        slopes = np.array([v[0] for v in values], dtype=float)
        intercepts = np.array([v[1] for v in values], dtype=float)

        slope = float(np.median(slopes))
        intercept = float(np.median(intercepts))
        if abs(slope) < 1e-6:
            return None

        x_bottom = int((y_bottom - intercept) / slope)
        x_top = int((y_top - intercept) / slope)
        return (x_bottom, y_bottom, x_top, y_top)

    def detect(self, frame: np.ndarray) -> LaneEstimate:
        """Estimate left/right boundaries and the runner's normalized center offset."""
        if frame is None or frame.size == 0:
            raise ValueError("frame must be a non-empty image")

        height, width = frame.shape[:2]
        runner_x = width / 2.0
        roi_top = int(height * self.roi_top_ratio)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)

        mask = np.zeros_like(edges)
        polygon = np.array(
            [[
                (0, height - 1),
                (int(width * 0.28), roi_top),
                (int(width * 0.72), roi_top),
                (width - 1, height - 1),
            ]],
            dtype=np.int32,
        )
        cv2.fillPoly(mask, polygon, 255)
        roi_edges = cv2.bitwise_and(edges, mask)

        raw_lines = cv2.HoughLinesP(
            roi_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=35,
            minLineLength=30,
            maxLineGap=45,
        )

        left_candidates: list[tuple[float, float]] = []
        right_candidates: list[tuple[float, float]] = []

        if raw_lines is not None:
            for item in raw_lines:
                # OpenCV commonly returns shape (1, 4); flattening avoids
                # version-dependent unpacking bugs.
                flat = np.asarray(item).reshape(-1)
                if flat.size < 4:
                    continue
                x1, y1, x2, y2 = [int(v) for v in flat[:4]]
                if x2 == x1:
                    continue

                slope = (y2 - y1) / (x2 - x1)
                if abs(slope) < 0.35:
                    continue
                intercept = y1 - slope * x1

                midpoint_x = (x1 + x2) / 2.0
                if slope < 0 and midpoint_x < width * 0.62:
                    left_candidates.append((slope, intercept))
                elif slope > 0 and midpoint_x > width * 0.38:
                    right_candidates.append((slope, intercept))

        y_bottom = height - 1
        y_top = roi_top
        left_line = self._fit_average_line(left_candidates, y_bottom, y_top)
        right_line = self._fit_average_line(right_candidates, y_bottom, y_top)

        confidence = 0.0
        lane_center_x: float | None = None
        normalized_offset: float | None = None

        if left_line is not None and right_line is not None:
            left_x = self._line_x_at_y(left_line, y_bottom)
            right_x = self._line_x_at_y(right_line, y_bottom)
            if left_x is not None and right_x is not None and right_x > left_x:
                raw_center = (left_x + right_x) / 2.0
                if self._smoothed_center is None:
                    self._smoothed_center = raw_center
                else:
                    a = self.smoothing_alpha
                    self._smoothed_center = a * raw_center + (1.0 - a) * self._smoothed_center

                lane_center_x = float(self._smoothed_center)
                lane_half_width = max((right_x - left_x) / 2.0, 1.0)
                # Positive = runner is to the RIGHT of lane center.
                normalized_offset = float((runner_x - lane_center_x) / lane_half_width)

                line_support = min(len(left_candidates), 5) + min(len(right_candidates), 5)
                confidence = min(1.0, 0.45 + 0.055 * line_support)

        elif left_line is not None or right_line is not None:
            confidence = 0.25

        return LaneEstimate(
            left_line=left_line,
            right_line=right_line,
            lane_center_x=lane_center_x,
            runner_x=runner_x,
            normalized_offset=normalized_offset,
            confidence=confidence,
        )
