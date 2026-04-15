# ============================================================
#  ldr.py — LDR (Photo-Resistor) ambient light sensor driver
#  NeuroBand IoT — Monitors bedroom light for sleep quality
#
#  Wiring (ESP32):
#    3.3V → 10kΩ resistor → GPIO34 (ADC) → LDR → GND
#
#  Note: GPIO34/35/36/39 are input-only on ESP32 — ideal for ADC.
#  The voltage divider output sits at GPIO34:
#    Dark room  → LDR high resistance → low voltage at ADC
#    Bright room → LDR low resistance  → high voltage at ADC
# ============================================================

from machine import ADC, Pin
from config  import LDR_ADC_PIN, LDR_ADC_ATTEN, ADC_MAX, ADC_VOLTAGE


class LDR:
    """
    Reads ambient light level via ADC voltage divider.

    Sleep threshold context:
      luxPercent < 5%   → IDEAL   (dark, supports melatonin production)
      5–30%             → DIM     (dim light, acceptable)
      > 30%             → BRIGHT  (disrupts circadian rhythm)
    """

    def __init__(self):
        self._adc = ADC(Pin(LDR_ADC_PIN))
        # ATTN_11DB allows 0–3.3V full range input
        self._adc.atten(ADC.ATTN_11DB)
        self._adc.width(ADC.WIDTH_12BIT)   # 0–4095
        print("[LDR] Initialized on GPIO{}.".format(LDR_ADC_PIN))

    def read(self) -> dict:
        """
        Returns a dict with lux_percent and voltage.
          lux_percent: 0 (dark) to 100 (maximum brightness)
          voltage:     0.0 to 3.3 V
        """
        # Average 5 readings to reduce ADC noise
        raw = sum(self._adc.read() for _ in range(5)) // 5

        voltage    = round((raw / ADC_MAX) * ADC_VOLTAGE, 4)
        lux_pct    = round((raw / ADC_MAX) * 100.0, 2)

        return {
            "lux_percent": lux_pct,
            "voltage":     voltage,
        }
