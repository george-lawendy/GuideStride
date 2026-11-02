# Reproducibility check

The repository was smoke-tested on the current software baseline before packaging.

## Automated tests

```text
6 passed
```

Coverage includes:

- two-boundary lane detection on synthetic frames
- lane-center offset sign convention
- stable/right-drift guidance behavior
- low-confidence suppression
- 10-feature vector construction

## End-to-end synthetic video run

Commands:

```bash
python scripts/generate_demo_video.py
python scripts/run_guidestride.py --video data/demo/demo_track.mp4 --save-video
```

Observed result:

```text
Generated frames: 720
Processed frames: 720
Structured CSV log: created successfully
Annotated output video: created successfully
Lane-center estimate available: 720 / 720 synthetic frames
```

This is a **software reproducibility check on a deterministic synthetic track**, not a real-world accuracy claim. Real camera/IMU performance and Raspberry Pi latency/FPS remain to be measured under defined test conditions.
