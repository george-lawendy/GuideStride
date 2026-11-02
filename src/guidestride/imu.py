"""Minimal MPU6050 interface for Raspberry Pi collection sessions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MPU6050Reading:
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float


class MPU6050:
    """Read scaled accelerometer and gyroscope values over I2C.

    The import of ``smbus2`` is intentionally delayed so the rest of the project
    remains runnable on macOS/Windows without Raspberry Pi hardware packages.
    """

    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    def __init__(self, bus_id: int = 1, address: int = 0x68) -> None:
        try:
            from smbus2 import SMBus
        except ImportError as exc:
            raise RuntimeError(
                "smbus2 is required for MPU6050 access. "
                "Install requirements-hardware.txt on the Raspberry Pi."
            ) from exc

        self.address = address
        self.bus = SMBus(bus_id)
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)

    def _read_i16(self, register: int) -> int:
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)
        value = (high << 8) | low
        return value - 65536 if value >= 32768 else value

    def read(self) -> MPU6050Reading:
        # Default MPU6050 ranges: ±2 g and ±250 deg/s.
        ax = self._read_i16(self.ACCEL_XOUT_H) / 16384.0
        ay = self._read_i16(self.ACCEL_XOUT_H + 2) / 16384.0
        az = self._read_i16(self.ACCEL_XOUT_H + 4) / 16384.0
        gx = self._read_i16(self.GYRO_XOUT_H) / 131.0
        gy = self._read_i16(self.GYRO_XOUT_H + 2) / 131.0
        gz = self._read_i16(self.GYRO_XOUT_H + 4) / 131.0
        return MPU6050Reading(ax=ax, ay=ay, az=az, gx=gx, gy=gy, gz=gz)

    def close(self) -> None:
        self.bus.close()
