"""Temporal drift-state estimation and guidance mapping."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Deque

import numpy as np


class DriftState(str, Enum):
    LEFT_DRIFT = "LEFT_DRIFT"
    STABLE = "STABLE"
    RIGHT_DRIFT = "RIGHT_DRIFT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class DriftEstimate:
    state: DriftState
    smoothed_offset: float | None
    offset_slope: float | None
    confidence: float
    guidance: str


class DriftEstimator:
    """Small interpretable temporal baseline used by the current demo.

    This is *not* the final ML classifier. It provides a deterministic baseline
    while labeled multimodal data is being collected.
    """

    def __init__(
        self,
        history_size: int = 8,
        stable_threshold: float = 0.08,
        low_confidence_threshold: float = 0.35,
    ) -> None:
        self.history: Deque[float] = deque(maxlen=history_size)
        self.stable_threshold = stable_threshold
        self.low_confidence_threshold = low_confidence_threshold

    def update(self, offset: float | None, lane_confidence: float) -> DriftEstimate:
        if offset is None or lane_confidence < self.low_confidence_threshold:
            return DriftEstimate(
                state=DriftState.UNKNOWN,
                smoothed_offset=None,
                offset_slope=None,
                confidence=lane_confidence,
                guidance="HOLD / LOW CONFIDENCE",
            )

        self.history.append(float(offset))
        values = np.asarray(self.history, dtype=float)
        smoothed = float(np.mean(values[-min(4, len(values)) :]))

        slope: float | None = None
        if len(values) >= 3:
            x = np.arange(len(values), dtype=float)
            slope = float(np.polyfit(x, values, deg=1)[0])

        # Offset is runner_x - lane_center_x, normalized by half lane width.
        # Positive => runner is right of center; negative => left of center.
        if abs(smoothed) <= self.stable_threshold:
            state = DriftState.STABLE
            guidance = "CENTERED"
        elif smoothed > self.stable_threshold:
            state = DriftState.RIGHT_DRIFT
            guidance = "MOVE LEFT"
        else:
            state = DriftState.LEFT_DRIFT
            guidance = "MOVE RIGHT"

        temporal_consistency = min(1.0, len(values) / max(self.history.maxlen or 1, 1))
        confidence = float(min(1.0, 0.7 * lane_confidence + 0.3 * temporal_consistency))

        return DriftEstimate(
            state=state,
            smoothed_offset=smoothed,
            offset_slope=slope,
            confidence=confidence,
            guidance=guidance,
        )
