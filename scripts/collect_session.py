#!/usr/bin/env python3
"""Collect synchronized raw camera and MPU6050 data on Raspberry Pi.

The collector intentionally records raw measurements only. Labels and derived
features should be generated offline so the original data remain reproducible.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from guidestride.imu import MPU6050  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--root", default="dataset/raw")
    parser.add_argument("--no-imu", action="store_true", help="Camera-only test mode")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_dir = Path(args.root) / session_id
    session_dir.mkdir(parents=True, exist_ok=False)

    cap = cv2.VideoCapture(args.camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, args.fps)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        str(session_dir / "video.mp4"),
        cv2.VideoWriter_fourcc(*"mp4v"),
        args.fps,
        (actual_width, actual_height),
    )
    if not writer.isOpened():
        raise RuntimeError("Could not create video writer")

    imu = None if args.no_imu else MPU6050()

    metadata = {
        "session_id": session_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "duration_requested_s": args.duration,
        "camera_index": args.camera_index,
        "fps_requested": args.fps,
        "frame_width": actual_width,
        "frame_height": actual_height,
        "imu_enabled": imu is not None,
        "labels_included": False,
        "derived_features_included": False,
    }
    (session_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("READY TO RECORD")
    input("Press Enter to start the collection session...")
    for count in (3, 2, 1):
        print(count)
        time.sleep(1)

    start = time.perf_counter()
    frame_index = 0

    with open(session_dir / "frames.csv", "w", newline="", encoding="utf-8") as frames_file, open(
        session_dir / "imu.csv", "w", newline="", encoding="utf-8"
    ) as imu_file:
        frames_log = csv.DictWriter(frames_file, fieldnames=["frame", "timestamp_s"])
        imu_log = csv.DictWriter(
            imu_file,
            fieldnames=["timestamp_s", "ax", "ay", "az", "gx", "gy", "gz"],
        )
        frames_log.writeheader()
        imu_log.writeheader()

        try:
            while True:
                now = time.perf_counter()
                elapsed = now - start
                if elapsed >= args.duration:
                    break

                ok, frame = cap.read()
                if not ok:
                    continue

                writer.write(frame)
                frames_log.writerow({"frame": frame_index, "timestamp_s": elapsed})
                frame_index += 1

                if imu is not None:
                    reading = imu.read()
                    imu_log.writerow(
                        {
                            "timestamp_s": elapsed,
                            "ax": reading.ax,
                            "ay": reading.ay,
                            "az": reading.az,
                            "gx": reading.gx,
                            "gy": reading.gy,
                            "gz": reading.gz,
                        }
                    )
        except KeyboardInterrupt:
            print("Collection stopped by user.")
        finally:
            cap.release()
            writer.release()
            if imu is not None:
                imu.close()

    print(f"Saved session: {session_dir.resolve()}")
    print(f"Captured frames: {frame_index}")


if __name__ == "__main__":
    main()
