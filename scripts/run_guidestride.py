#!/usr/bin/env python3
"""Run the current GuideStride perception prototype on a video."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from guidestride.drift import DriftEstimator  # noqa: E402
from guidestride.lane_detection import LaneDetector  # noqa: E402
from guidestride.visualization import draw_overlay  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Input video path")
    parser.add_argument("--log", default="outputs/run_log.csv")
    parser.add_argument("--output-video", default="outputs/guidestride_demo.mp4")
    parser.add_argument("--save-video", action="store_true")
    parser.add_argument("--display", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.video)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_video).parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {input_path}")

    fps_in = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = None
    if args.save_video:
        writer = cv2.VideoWriter(
            str(args.output_video),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps_in,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError("Could not create output video writer")

    detector = LaneDetector()
    drift_estimator = DriftEstimator()

    fields = [
        "frame",
        "timestamp_s",
        "lane_center_x",
        "runner_x",
        "normalized_offset",
        "lane_confidence",
        "smoothed_offset",
        "offset_slope",
        "drift_state",
        "guidance",
        "processing_fps",
    ]

    frame_idx = 0
    with open(args.log, "w", newline="", encoding="utf-8") as f:
        log = csv.DictWriter(f, fieldnames=fields)
        log.writeheader()

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            started = time.perf_counter()
            lane = detector.detect(frame)
            drift = drift_estimator.update(lane.normalized_offset, lane.confidence)
            elapsed = max(time.perf_counter() - started, 1e-9)
            processing_fps = 1.0 / elapsed

            annotated = draw_overlay(frame, lane, drift, fps=processing_fps)

            log.writerow(
                {
                    "frame": frame_idx,
                    "timestamp_s": frame_idx / fps_in,
                    "lane_center_x": lane.lane_center_x,
                    "runner_x": lane.runner_x,
                    "normalized_offset": lane.normalized_offset,
                    "lane_confidence": lane.confidence,
                    "smoothed_offset": drift.smoothed_offset,
                    "offset_slope": drift.offset_slope,
                    "drift_state": drift.state.value,
                    "guidance": drift.guidance,
                    "processing_fps": processing_fps,
                }
            )

            if writer is not None:
                writer.write(annotated)
            if args.display:
                cv2.imshow("GuideStride", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_idx += 1

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()

    print(f"Processed frames: {frame_idx}")
    print(f"Saved log: {Path(args.log).resolve()}")
    if args.save_video:
        print(f"Saved video: {Path(args.output_video).resolve()}")


if __name__ == "__main__":
    main()
