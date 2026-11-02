from guidestride.features import IMUSample, build_feature_vector


def test_builds_ten_feature_baseline() -> None:
    vector = build_feature_vector(
        normalized_offset=0.2,
        smoothed_offset=0.15,
        offset_slope=0.01,
        lane_confidence=0.8,
        imu=IMUSample(ax=1, ay=2, az=3, gx=4, gy=5, gz=6),
    )
    values = vector.to_dict()
    assert len(values) == 10
    assert values["ax"] == 1
    assert values["gz"] == 6
