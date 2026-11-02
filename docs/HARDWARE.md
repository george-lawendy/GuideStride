# Hardware integration

## Current planned hardware

- Raspberry Pi 4 (4 GB)
- 5 MP Rev 1.3 camera
- MPU6050 IMU
- two vibration motors + appropriate driver circuitry
- portable power source

## MPU6050 wiring

| MPU6050 | Raspberry Pi 4 |
|---|---|
| VCC | Pin 1 (3.3 V) |
| GND | Pin 6 (GND) |
| SDA | GPIO 2 / Pin 3 |
| SCL | GPIO 3 / Pin 5 |

Enable I2C on the Raspberry Pi before running the collector.

## Collection workflow

1. Connect camera and MPU6050.
2. Install `requirements-hardware.txt`.
3. Start `scripts/collect_session.py`.
4. Confirm the terminal prints `READY TO RECORD`.
5. Press Enter in the same terminal.
6. The 3-second countdown begins.
7. Recording stops automatically after the requested duration.
8. Use `Ctrl+C` only as an emergency stop.

## Current integration status

The collection software and wiring plan are prepared. Repeated synchronized real-world sessions and vibration-motor validation remain in progress.
