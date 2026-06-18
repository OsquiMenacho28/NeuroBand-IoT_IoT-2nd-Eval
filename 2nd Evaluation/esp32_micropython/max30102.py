# ============================================================
#  max30102.py — MAX30102 Heart Rate & SpO2 sensor driver
#  NeuroBand IoT — Optical pulse oximetry for sleep monitoring
#
#  I2C Address: 0x57 (fixed)
#  Wiring (ESP32 — shared I2C bus with MPU6050):
#    VIN  → 3.3V
#    GND  → GND
#    SDA  → GPIO21
#    SCL  → GPIO22
#
#  Note: This driver uses a simplified SpO2 estimation.
#        For clinical accuracy, use the full Maxim algorithm.
# ============================================================

import struct
import math
import time


class MAX30102:
    I2C_ADDR = 0x57

    # Key registers
    _REG_INT_STATUS_1   = 0x00
    _REG_FIFO_WR_PTR    = 0x04
    _REG_FIFO_RD_PTR    = 0x06
    _REG_FIFO_DATA      = 0x07
    _REG_FIFO_CONFIG    = 0x08
    _REG_MODE_CONFIG    = 0x09
    _REG_SPO2_CONFIG    = 0x0A
    _REG_LED1_PA        = 0x0C   # Red LED pulse amplitude
    _REG_LED2_PA        = 0x0D   # IR LED pulse amplitude
    _REG_PART_ID        = 0xFF

    def __init__(self, i2c, addr: int = 0x57):
        self._i2c  = i2c
        self._addr = addr

        # Buffers for running average (last N samples)
        self._ir_buf  = []
        self._red_buf = []
        self._buf_size = 50

        self._init_sensor()

    def _init_sensor(self):
        """Configure MAX30102 for SpO2 + HR mode."""
        part_id = self._read_byte(self._REG_PART_ID)
        if part_id != 0x15:
            raise RuntimeError(
                "[MAX30102] Unexpected PART_ID=0x{:02X}. Check wiring.".format(part_id)
            )

        # Reset
        self._write_byte(self._REG_MODE_CONFIG, 0x40)
        time.sleep_ms(100)

        # FIFO config: sample average = 4, roll-over enabled, almost full = 17
        self._write_byte(self._REG_FIFO_CONFIG, 0x4F)

        # SpO2 mode (both LEDs active)
        self._write_byte(self._REG_MODE_CONFIG, 0x03)

        # SpO2 config: ADC range=4096nA, sample rate=100Hz, pulse width=411µs
        self._write_byte(self._REG_SPO2_CONFIG, 0x27)

        # LED pulse amplitude: ~7mA for sleep sensing (low power)
        self._write_byte(self._REG_LED1_PA, 0x24)  # Red
        self._write_byte(self._REG_LED2_PA, 0x24)  # IR

        # Reset FIFO pointers
        self._write_byte(self._REG_FIFO_WR_PTR, 0x00)
        self._write_byte(self._REG_FIFO_RD_PTR, 0x00)

        print("[MAX30102] Initialized. PART_ID=0x15")

    def read_sample(self) -> dict | None:
        """
        Read one FIFO sample from MAX30102.
        Returns dict with ir_value, red_value, heart_rate, spo2.
        Returns None if FIFO is empty.
        """
        # Check FIFO write pointer
        wr_ptr = self._read_byte(self._REG_FIFO_WR_PTR)
        rd_ptr = self._read_byte(self._REG_FIFO_RD_PTR)

        if wr_ptr == rd_ptr:
            return None  # FIFO empty

        # Read 6 bytes: 3 bytes red + 3 bytes IR
        data = self._i2c.readfrom_mem(self._addr, self._REG_FIFO_DATA, 6)

        red_raw = ((data[0] & 0x03) << 16) | (data[1] << 8) | data[2]
        ir_raw  = ((data[3] & 0x03) << 16) | (data[4] << 8) | data[5]

        # Accumulate buffer for averaging
        self._red_buf.append(red_raw)
        self._ir_buf.append(ir_raw)
        if len(self._red_buf) > self._buf_size:
            self._red_buf.pop(0)
            self._ir_buf.pop(0)

        # Need at least 10 samples for estimation
        if len(self._ir_buf) < 10:
            return {
                "ir_value":   ir_raw,
                "red_value":  red_raw,
                "heart_rate": 0.0,
                "spo2":       0.0,
            }

        hr, spo2 = self._estimate_hr_spo2()

        return {
            "ir_value":   ir_raw,
            "red_value":  red_raw,
            "heart_rate": round(hr,   1),
            "spo2":       round(spo2, 1),
        }

    def _estimate_hr_spo2(self) -> tuple:
        """
        Simplified AC/DC ratio estimation for SpO2.
        Heart rate estimated from IR peak detection.
        """
        ir  = self._ir_buf
        red = self._red_buf

        ir_dc  = sum(ir)  / len(ir)
        red_dc = sum(red) / len(red)

        if ir_dc == 0 or red_dc == 0:
            return 0.0, 0.0

        ir_ac  = math.sqrt(sum((v - ir_dc)  ** 2 for v in ir)  / len(ir))
        red_ac = math.sqrt(sum((v - red_dc) ** 2 for v in red) / len(red))

        # R ratio (Ratio-of-Ratios method)
        if ir_ac == 0:
            return 0.0, 0.0

        r = (red_ac / red_dc) / (ir_ac / ir_dc)

        # Linear approximation (Maxim AN6409 simplified)
        spo2 = max(0.0, min(100.0, 110.0 - 25.0 * r))

        # Heart rate: count zero-crossings in IR AC signal
        crossings = 0
        for i in range(1, len(ir)):
            if (ir[i] - ir_dc) * (ir[i - 1] - ir_dc) < 0:
                crossings += 1

        # Each crossing = half period; assume 100Hz sample rate
        hr = (crossings / 2.0) * (60.0 * 100.0 / len(ir))
        hr = max(30.0, min(200.0, hr))  # clamp to physiological range

        return hr, spo2

    def _write_byte(self, reg: int, value: int):
        self._i2c.writeto_mem(self._addr, reg, bytes([value]))

    def _read_byte(self, reg: int) -> int:
        return self._i2c.readfrom_mem(self._addr, reg, 1)[0]
