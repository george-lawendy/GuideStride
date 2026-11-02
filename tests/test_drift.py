from guidestride.drift import DriftEstimator, DriftState


def test_stable_state_near_center() -> None:
    estimator = DriftEstimator()
    result = estimator.update(0.02, 0.9)
    assert result.state == DriftState.STABLE
    assert result.guidance == "CENTERED"


def test_right_drift_requests_move_left() -> None:
    estimator = DriftEstimator()
    result = None
    for value in [0.12, 0.15, 0.16, 0.18]:
        result = estimator.update(value, 0.9)
    assert result is not None
    assert result.state == DriftState.RIGHT_DRIFT
    assert result.guidance == "MOVE LEFT"


def test_low_confidence_suppresses_guidance() -> None:
    estimator = DriftEstimator()
    result = estimator.update(0.4, 0.1)
    assert result.state == DriftState.UNKNOWN
    assert "LOW CONFIDENCE" in result.guidance
