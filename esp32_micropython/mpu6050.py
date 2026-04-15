# ============================================================
#  mpu6050.py — MPU6050 Accelerometer & Gyroscope driver
#  NeuroBand IoT — 6-axis motion sensor for sleep detection
#
#  I2C Address: 0x68 (AD0=GND) or 0x69 (AD0=3.3V)
#  Wiring (ESP32):
#    VCC  → 3.3V
#    GND  → GND
#    SDA  → GPIO21
#    SCL  → GPIO22
#    AD0  → GND (sets I2C address to 0x68)
# ============================================================

import struct
import math


class MPU6050:
    # Register map
    _REG_PWR_MGMT_1   = 0x6B
    _REG_ACCEL_CONFIG  = 0x1C
    _REG_GYRO_CONFIG   = 0x1B
    _REG_ACCEL_XOUT_H  = 0x3B
    _REG_GYRO_XOUT_H   = 0x43
    _REG_WHO_AM_I      = 0x75

    # Sensitivity scales
    _ACCEL_SCALE  = 16384.0  # ±2g range  → LSB/g
    _GYRO_SCALE   = 131.0    # ±250°/s    → LSB/(°/s)

    I2C_ADDR = 0x68

    def __init__(self, i2c, addr: int = 0x68):
        self._i2c = i2c
        self._addr = addr
        self._init_sensor()

    def _init_sensor(self):
        """Wake up MPU6050 and configure ranges."""
        # Wake up (clear sleep bit)
        self._write_byte(self._REG_PWR_MGMT_1, 0x00)

        # Accelerometer: ±2g range
        self._write_byte(self._REG_ACCEL_CONFIG, 0x00)

        # Gyroscope: ±250°/s range
        self._write_byte(self._REG_GYRO_CONFIG, 0x00)

        # Verify device ID
        who = self._read_byte(self._REG_WHO_AM_I)
        if who != 0x68:
            raise RuntimeError(
                "[MPU6050] Device not found. WHO_AM_I=0x{:02X} (expected 0x68)".format(who)
            )
        print("[MPU6050] Initialized. WHO_AM_I=0x{:02X}".format(who))

    def read_raw(self) -> dict:
        """
        Read all 6 axes (accel XYZ + gyro XYZ) in one I2C burst.
        Returns a dict with scaled physical values:
          accel_{x,y,z}: g-force
          gyro_{x,y,z}: degrees/second
          accel_magnitude: |accel| in g (scalar)
        """
        # Read 14 bytes starting at ACCEL_XOUT_H
        data = self._i2c.readfrom_mem(self._addr, self._REG_ACCEL_XOUT_H, 14)

        # Unpack 7 signed 16-bit values: ax, ay, az, temp, gx, gy, gz
        values = struct.unpack(">hhhhhhh", data)

        ax = values[0] / self._ACCEL_SCALE
        ay = values[1] / self._ACCEL_SCALE
        az = values[2] / self._ACCEL_SCALE
        gx = values[4] / self._GYRO_SCALE
        gy = values[5] / self._GYRO_SCALE
        gz = values[6] / self._GYRO_SCALE

        magnitude = math.sqrt(ax * ax + ay * ay + az * az)

        return {
            "accel_x":         round(ax, 4),
            "accel_y":         round(ay, 4),
            "accel_z":         round(az, 4),
            "gyro_x":          round(gx, 4),
            "gyro_y":          round(gy, 4),
            "gyro_z":          round(gz, 4),
            "accel_magnitude": round(magnitude, 4),
        }

    def _write_byte(self, reg: int, value: int):
        self._i2c.writeto_mem(self._addr, reg, bytes([value]))

    def _read_byte(self, reg: int) -> int:
        return self._i2c.readfrom_mem(self._addr, reg, 1)[0]
