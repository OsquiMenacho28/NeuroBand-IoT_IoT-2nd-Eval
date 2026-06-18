# ============================================================
#  wifi.py — WiFi connection manager for ESP32
#  NeuroBand IoT Project
# ============================================================

import network
import time
from config import WIFI_SSID, WIFI_PASSWORD


def connect() -> str:
    """
    Connect to the WiFi network defined in config.py.
    Returns the assigned IP address as a string.
    Raises RuntimeError if connection fails after 20 seconds.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Already connected — return current IP
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("[WiFi] Already connected. IP: {}".format(ip))
        return ip

    print("[WiFi] Connecting to '{}'...".format(WIFI_SSID))
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    attempts = 0
    while not wlan.isconnected():
        time.sleep(0.5)
        attempts += 1
        if attempts % 4 == 0:
            print("[WiFi] Still connecting... ({:.0f}s)".format(attempts * 0.5))
        if attempts > 40:
            raise RuntimeError(
                "[WiFi] Failed to connect to '{}' after 20s.".format(WIFI_SSID)
            )

    ip = wlan.ifconfig()[0]
    print("[WiFi] Connected! Device IP: {}".format(ip))
    return ip


def is_connected() -> bool:
    """Check if WiFi is currently connected."""
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()


def reconnect_if_needed() -> bool:
    """Attempt reconnection if WiFi dropped. Returns True if connected."""
    if is_connected():
        return True
    print("[WiFi] Connection lost. Reconnecting...")
    try:
        connect()
        return True
    except RuntimeError as e:
        print("[WiFi] Reconnection failed: {}".format(e))
        return False
