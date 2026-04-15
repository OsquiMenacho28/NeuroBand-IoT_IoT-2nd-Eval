# ============================================================
#  main.py — NeuroBand IoT ESP32 Main Program
#  
#  Reads MPU6050, MAX30102 and LDR sensors continuously
#  and sends data to the Spring Boot backend in real-time.
#
#  Flash all files to ESP32:
#    config.py, wifi.py, mpu6050.py, max30102.py, ldr.py,
#    http_client.py, main.py
#
#  Tools: Thonny IDE or mpremote
# ============================================================

import time
import machine
from machine import I2C, Pin

import wifi
import http_client
from mpu6050    import MPU6050
from max30102   import MAX30102
from ldr        import LDR
from config     import (
    I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQ,
    SAMPLE_INTERVAL_MS, DEVICE_ID
)

# ── Built-in LED (GPIO2 on most ESP32 boards) ─────────────────
LED = Pin(2, Pin.OUT)

# ── Banner ────────────────────────────────────────────────────

def print_banner():
    print()
    print("=" * 52)
    print("   NeuroBand IoT — Sleep Monitoring System")
    print("   Device: {}".format(DEVICE_ID))
    print("=" * 52)
    print()

# ── LED helpers ───────────────────────────────────────────────

def blink(times: int = 1, delay_ms: int = 100):
    """Blink built-in LED to signal activity."""
    for _ in range(times):
        LED.on()
        time.sleep_ms(delay_ms)
        LED.off()
        time.sleep_ms(delay_ms)

def led_error():
    """3 rapid blinks = error."""
    blink(3, 80)

def led_ok():
    """1 slow blink = success."""
    blink(1, 300)

# ── Connection phase ──────────────────────────────────────────

def connect_phase():
    """Connect to WiFi and verify server availability."""
    print("[BOOT] Connecting to WiFi...")
    blink(2, 200)

    try:
        ip = wifi.connect()
        led_ok()
    except RuntimeError as e:
        print("[BOOT] ERROR: {}".format(e))
        led_error()
        raise

    print("[BOOT] Checking server availability...")
    for attempt in range(1, 6):
        if http_client.check_server():
            print("[BOOT] Server is online. ✓")
            led_ok()
            return
        print("[BOOT] Attempt {}/5 — server not responding, retrying...".format(attempt))
        time.sleep(2)

    raise RuntimeError("[BOOT] Server unreachable after 5 attempts.")

# ── Sensor initialization ─────────────────────────────────────

def init_sensors():
    """Initialize I2C bus and all three sensors."""
    print("[SENSORS] Initializing I2C bus (SDA={}, SCL={}, {}kHz)...".format(
        I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQ // 1000
    ))

    i2c = I2C(0, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=I2C_FREQ)

    # Scan for I2C devices
    devices = i2c.scan()
    print("[I2C] Devices found: {}".format(
        ["0x{:02X}".format(d) for d in devices]
    ))

    sensors = {}

    # MPU6050 (0x68)
    try:
        sensors["mpu"] = MPU6050(i2c)
        print("[SENSORS] MPU6050 ✓")
    except Exception as e:
        print("[SENSORS] MPU6050 FAILED: {}".format(e))
        sensors["mpu"] = None

    # MAX30102 (0x57)
    try:
        sensors["max"] = MAX30102(i2c)
        print("[SENSORS] MAX30102 ✓")
    except Exception as e:
        print("[SENSORS] MAX30102 FAILED: {}".format(e))
        sensors["max"] = None

    # LDR (ADC — no I2C)
    try:
        sensors["ldr"] = LDR()
        print("[SENSORS] LDR ✓")
    except Exception as e:
        print("[SENSORS] LDR FAILED: {}".format(e))
        sensors["ldr"] = None

    return sensors

# ── Main reading loop ─────────────────────────────────────────

def reading_loop(sensors: dict):
    """
    Continuously reads all sensors and sends data to the server.
    Runs indefinitely until interrupted (Ctrl+C in Thonny).
    """
    print()
    print("[LOOP] Starting sensor loop. Press Ctrl+C to stop.")
    print("[LOOP] Sampling every {}ms".format(SAMPLE_INTERVAL_MS))
    print("-" * 52)

    cycle   = 0
    errors  = 0

    while True:
        cycle += 1
        t_start = time.ticks_ms()

        print("\n[#{}] {}".format(cycle, time.localtime()))

        # ── MPU6050 ──────────────────────────────────────────
        if sensors["mpu"]:
            try:
                mpu_data = sensors["mpu"].read_raw()
                ok = http_client.send_mpu6050(mpu_data)
                status = "✓ sent" if ok else "✗ send failed"
                print("  MPU6050  | mag={:.4f}g | ax={:.3f} ay={:.3f} az={:.3f} | {}".format(
                    mpu_data["accel_magnitude"],
                    mpu_data["accel_x"], mpu_data["accel_y"], mpu_data["accel_z"],
                    status
                ))
                if not ok:
                    errors += 1
            except Exception as e:
                print("  MPU6050  | READ ERROR: {}".format(e))
                errors += 1

        # ── MAX30102 ─────────────────────────────────────────
        if sensors["max"]:
            try:
                max_data = sensors["max"].read_sample()
                if max_data:
                    ok = http_client.send_max30102(max_data)
                    status = "✓ sent" if ok else "✗ send failed"
                    print("  MAX30102 | HR={:.1f}bpm | SpO2={:.1f}% | IR={} | {}".format(
                        max_data["heart_rate"], max_data["spo2"],
                        max_data["ir_value"], status
                    ))
                    if not ok:
                        errors += 1
                else:
                    print("  MAX30102 | FIFO empty — warming up...")
            except Exception as e:
                print("  MAX30102 | READ ERROR: {}".format(e))
                errors += 1

        # ── LDR ──────────────────────────────────────────────
        if sensors["ldr"]:
            try:
                ldr_data = sensors["ldr"].read()
                ok = http_client.send_ldr(ldr_data)
                status = "✓ sent" if ok else "✗ send failed"
                print("  LDR      | light={:.1f}% | voltage={:.3f}V | {}".format(
                    ldr_data["lux_percent"], ldr_data["voltage"], status
                ))
                if not ok:
                    errors += 1
            except Exception as e:
                print("  LDR      | READ ERROR: {}".format(e))
                errors += 1

        # ── LED feedback ──────────────────────────────────────
        LED.on()  # solid = alive

        # ── WiFi watchdog ─────────────────────────────────────
        if not wifi.is_connected():
            print("  [!] WiFi lost — reconnecting...")
            LED.off()
            wifi.reconnect_if_needed()

        # ── Timing ────────────────────────────────────────────
        elapsed = time.ticks_diff(time.ticks_ms(), t_start)
        wait    = max(0, SAMPLE_INTERVAL_MS - elapsed)
        time.sleep_ms(wait)

# ── Entry point ───────────────────────────────────────────────

def main():
    print_banner()

    # Phase 1: WiFi + server
    connect_phase()

    # Phase 2: Sensors
    sensors = init_sensors()

    active = sum(1 for v in sensors.values() if v is not None)
    print("\n[BOOT] {} / 3 sensors active. Starting data collection...".format(active))
    blink(active, 150)
    time.sleep(1)

    # Phase 3: Main loop
    try:
        reading_loop(sensors)
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted by user. Goodbye!")
        LED.off()


# Run immediately on ESP32 boot
main()
