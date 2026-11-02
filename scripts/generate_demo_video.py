#!/usr/bin/env python3
"""Generate a deterministic synthetic running-path video for local testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/demo/demo_track.mp4")
    parser.add_argument("--frames", type=int, default=720)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output), fourcc, args.fps, (args.width, args.height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create video writer for {output}")

    horizon_y = int(args.height * 0.52)
    base_half_width = int(args.width * 0.29)
    top_half_width = int(args.width * 0.08)

    for i in range(args.frames):
        phase = 2.0 * np.pi * i / max(args.frames - 1, 1)
        lane_shift = int(np.sin(phase * 1.4) * args.width * 0.07)
        lane_shift += int(np.sin(phase * 0.35) * args.width * 0.025)

        frame = np.full((args.height, args.width, 3), 48, dtype=np.uint8)
        cv2.rectangle(frame, (0, horizon_y), (args.width, args.height), (68, 68, 68), -1)

        cx = args.width // 2 + lane_shift
        left_bottom = (cx - base_half_width, args.height - 1)
        right_bottom = (cx + base_half_width, args.height - 1)
        left_top = (cx - top_half_width, horizon_y)
        right_top = (cx + top_half_width, horizon_y)

        cv2.line(frame, left_bottom, left_top, (245, 245, 245), 8, cv2.LINE_AA)
        cv2.line(frame, right_bottom, right_top, (245, 245, 245), 8, cv2.LINE_AA)

        # Add subtle deterministic texture to avoid an unrealistically empty frame.
        for k in range(18):
            x = (73 * k + 13 * i) % args.width
            y = horizon_y + ((47 * k + 7 * i) % max(args.height - horizon_y, 1))
            cv2.circle(frame, (int(x), int(y)), 1, (90, 90, 90), -1)

        writer.write(frame)

    writer.release()
    print(f"Generated {args.frames} frames: {output.resolve()}")


if __name__ == "__main__":
    main()
