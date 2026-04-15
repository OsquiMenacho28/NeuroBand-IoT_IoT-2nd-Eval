# ============================================================
#  http_client.py — HTTP sender for NeuroBand IoT ESP32
#  Posts sensor readings to the Spring Boot REST API
# ============================================================

import urequests
import ujson
from config import SERVER_HOST, SERVER_PORT, DEVICE_ID, HTTP_TIMEOUT_S

_BASE = "http://{}:{}".format(SERVER_HOST, SERVER_PORT)
_HEADERS = {"Content-Type": "application/json"}


def _post(endpoint: str, payload: dict) -> bool:
    """
    POST JSON payload to /api/{endpoint}.
    Returns True on success (HTTP 201), False on error.
    """
    url = "{}/api/{}".format(_BASE, endpoint)
    try:
        body = ujson.dumps(payload)
        resp = urequests.post(url, data=body, headers=_HEADERS,
                              timeout=HTTP_TIMEOUT_S)
        ok = resp.status_code in (200, 201)
        resp.close()
        return ok
    except OSError as e:
        print("[HTTP] Network error → {}: {}".format(endpoint, e))
        return False
    except Exception as e:
        print("[HTTP] Unexpected error → {}: {}".format(endpoint, e))
        return False


def send_mpu6050(data: dict) -> bool:
    """Send MPU6050 reading to POST /api/mpu6050"""
    return _post("mpu6050", {
        "deviceId":        DEVICE_ID,
        "accelX":          data["accel_x"],
        "accelY":          data["accel_y"],
        "accelZ":          data["accel_z"],
        "gyroX":           data["gyro_x"],
        "gyroY":           data["gyro_y"],
        "gyroZ":           data["gyro_z"],
    })


def send_max30102(data: dict) -> bool:
    """Send MAX30102 reading to POST /api/max30102"""
    # Skip if sensor hasn't warmed up yet
    if data["heart_rate"] == 0.0 or data["spo2"] == 0.0:
        return True  # silently skip — not a real failure
    return _post("max30102", {
        "deviceId":   DEVICE_ID,
        "heartRate":  data["heart_rate"],
        "spo2":       data["spo2"],
        "irValue":    data["ir_value"],
        "redValue":   data["red_value"],
    })


def send_ldr(data: dict) -> bool:
    """Send LDR reading to POST /api/ldr"""
    return _post("ldr", {
        "deviceId":   DEVICE_ID,
        "luxPercent": data["lux_percent"],
        "voltage":    data["voltage"],
    })


def check_server() -> bool:
    """Ping the backend health endpoint. Returns True if reachable."""
    try:
        resp = urequests.get("{}/api/status".format(_BASE),
                             timeout=HTTP_TIMEOUT_S)
        ok = resp.status_code == 200
        resp.close()
        return ok
    except Exception:
        return False
