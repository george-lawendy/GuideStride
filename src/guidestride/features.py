"""Feature engineering utilities for GuideStride multimodal classification."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class IMUSample:
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0
    gx: float = 0.0
    gy: float = 0.0
    gz: float = 0.0


@dataclass(frozen=True)
class FeatureVector:
    normalized_offset: float
    smoothed_offset: float
    offset_slope: float
    lane_confidence: float
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def build_feature_vector(
    normalized_offset: float,
    smoothed_offset: float | None,
    offset_slope: float | None,
    lane_confidence: float,
    imu: IMUSample | None = None,
) -> FeatureVector:
    """Create the planned 10-feature baseline vector.

    Missing temporal values are represented as 0.0 for this baseline; a future
    training pipeline may add explicit missingness indicators after experiments.
    """
    imu = imu or IMUSample()
    return FeatureVector(
        normalized_offset=float(normalized_offset),
        smoothed_offset=float(smoothed_offset or 0.0),
        offset_slope=float(offset_slope or 0.0),
        lane_confidence=float(lane_confidence),
        ax=float(imu.ax),
        ay=float(imu.ay),
        az=float(imu.az),
        gx=float(imu.gx),
        gy=float(imu.gy),
        gz=float(imu.gz),
    )
