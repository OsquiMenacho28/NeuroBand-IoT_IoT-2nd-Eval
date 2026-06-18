# ============================================================
#  main.py — ESP32-C3 Mini  |  MicroPython
#  Sensores → MQTT sobre WebSocket SSL
#  Broker: wss://iot2.ruwaylabs.lat/mqtt  (puerto 443)
# ============================================================

import time
import json
import network
import machine
from machine import Pin, ADC, SoftI2C
import dht
from mqtt_ws import MQTTWebsocketClient

# ── WiFi ─────────────────────────────────────────────────────
# Agrega redes de respaldo si tienes más de una disponible
WIFI_SSIDS  = ["", "", ""]
WIFI_PASSES = ["", "", ""]

# ── MQTT / WebSocket ─────────────────────────────────────────
MQTT_BROKER  = "iot2.ruwaylabs.lat"
MQTT_PORT    = 443
MQTT_USER    = "esp32user"
MQTT_PASS    = "ABCabc123"
MQTT_TOPIC   = b"proyecto/esp32_01/sensores"
MQTT_CLIENT  = "esp32_01"

# ── Pines ────────────────────────────────────────────────────
I2C_SDA = 8
I2C_SCL = 9
DHT_PIN = 10
LDR_PIN = 2

# ── Periféricos ──────────────────────────────────────────────
i2c        = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
sensor_dht = dht.DHT22(Pin(DHT_PIN))
ldr        = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)

# ── Direcciones I2C ──────────────────────────────────────────
MPU_ADDR      = 0x68
MAX30102_ADDR = 0x57
MAX30205_ADDR = 0x4c

INTERVALO_SEG = 2


# ════════════════════════════════════════════════════════════
#  WIFI  (corregido: scan → disconnect → mejor red → connect)
# ════════════════════════════════════════════════════════════
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()          # limpia cualquier conexión colgada
    time.sleep(0.5)

    if wlan.isconnected():
        print("  WiFi ya conectado:", wlan.ifconfig()[0])
        return wlan

    print("  Escaneando redes WiFi...")
    networks = wlan.scan()

    if len(networks) == 0:
        print("  ✗ No se encontraron redes.")
        return None

    maxRSSI   = -1000
    bestIdx   = -1

    for net in networks:
        ssid = net[0].decode('utf-8')
        rssi = net[3]
        print("    Red encontrada: {} (RSSI: {})".format(ssid, rssi))
        for j, known_ssid in enumerate(WIFI_SSIDS):
            if known_ssid and ssid == known_ssid and rssi > maxRSSI:
                maxRSSI = rssi
                bestIdx = j

    if bestIdx == -1:
        print("  ✗ Ninguna red conocida encontrada.")
        return None

    print("  Conectando a '{}' (RSSI: {})".format(WIFI_SSIDS[bestIdx], maxRSSI), end="")
    wlan.connect(WIFI_SSIDS[bestIdx], WIFI_PASSES[bestIdx])

    # Espera 10 segundos
    max_intentos = 20
    intentos = 0

    while not wlan.isconnected() and intentos < max_intentos:
        time.sleep(0.5)
        print(".", end="")
        intentos += 1

    if not wlan.isconnected():
        print("\n  ✗ No se pudo conectar al Wi-Fi.")
        wlan.disconnect()
        return None

    print("\n  ✓ IP: {}".format(wlan.ifconfig()[0]))
    return wlan


# ════════════════════════════════════════════════════════════
#  MQTT
# ════════════════════════════════════════════════════════════
mqtt_client = None

def conectar_mqtt():
    global mqtt_client
    try:
        client = MQTTWebsocketClient(
            MQTT_CLIENT,
            MQTT_BROKER,
            port=MQTT_PORT,
            user=MQTT_USER,
            password=MQTT_PASS,
            keepalive=60,
            ssl=True,
            ssl_params={}
        )
        client.connect()
        mqtt_client = client
        print("  ✓ MQTT WebSocket conectado a {}:{}".format(MQTT_BROKER, MQTT_PORT))
        return client
    except Exception as e:
        print("  ✗ MQTT error: {}".format(e))
        mqtt_client = None
        return None

def publicar(payload_dict):
    global mqtt_client
    try:
        msg = json.dumps(payload_dict)
        mqtt_client.publish(MQTT_TOPIC, msg.encode())
        print("  ✓ MQTT publicado ({} bytes)".format(len(msg)))
        return True
    except Exception as e:
        print("  ✗ Publish error: {} — reconectando...".format(e))
        mqtt_client = None
        conectar_mqtt()
        return False


# ════════════════════════════════════════════════════════════
#  SENSORES
# ════════════════════════════════════════════════════════════
def mpu6050_init():
    i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
    time.sleep_ms(100)

def mpu6050_leer():
    data = i2c.readfrom_mem(MPU_ADDR, 0x3B, 14)
    def s(h, l):
        v = (h << 8) | l
        return v - 65536 if v >= 32768 else v
    return {
        "ax": round(s(data[0],  data[1])  / 16384.0, 3),
        "ay": round(s(data[2],  data[3])  / 16384.0, 3),
        "az": round(s(data[4],  data[5])  / 16384.0, 3),
        "gx": round(s(data[8],  data[9])  / 131.0,   2),
        "gy": round(s(data[10], data[11]) / 131.0,   2),
        "gz": round(s(data[12], data[13]) / 131.0,   2),
    }

def max30102_init():
    i2c.writeto_mem(MAX30102_ADDR, 0x09, b'\x40')
    time.sleep_ms(100)
    i2c.writeto_mem(MAX30102_ADDR, 0x08, b'\x4F')
    i2c.writeto_mem(MAX30102_ADDR, 0x09, b'\x03')
    i2c.writeto_mem(MAX30102_ADDR, 0x0A, b'\x27')
    i2c.writeto_mem(MAX30102_ADDR, 0x0C, b'\x24')
    i2c.writeto_mem(MAX30102_ADDR, 0x0D, b'\x24')

def max30102_leer():
    wr = i2c.readfrom_mem(MAX30102_ADDR, 0x04, 1)[0] & 0x1F
    rd = i2c.readfrom_mem(MAX30102_ADDR, 0x06, 1)[0] & 0x1F
    if wr == rd:
        return {"rojo_raw": None, "ir_raw": None}
    data = i2c.readfrom_mem(MAX30102_ADDR, 0x07, 6)
    rojo = ((data[0] & 0x03) << 16) | (data[1] << 8) | data[2]
    ir   = ((data[3] & 0x03) << 16) | (data[4] << 8) | data[5]
    return {"rojo_raw": rojo, "ir_raw": ir}

def max30205_leer():
    data = i2c.readfrom_mem(MAX30205_ADDR, 0x00, 2)
    raw = (data[0] << 8) | data[1]
    if raw >= 32768:
        raw -= 65536
    return {"temp_corporal_C": round(raw * 0.00390625, 2)}

def dht22_leer():
    sensor_dht.measure()
    return {
        "temp_ambiente_C": sensor_dht.temperature(),
        "humedad_pct":     sensor_dht.humidity()
    }

def ldr_leer():
    raw = ldr.read()
    return {"raw": raw, "luz_pct": round((raw / 4095) * 100, 1)}

def leer_todos():
    datos = {"timestamp": time.time()}
    for nombre, fn in [
        ("mpu6050",  mpu6050_leer),
        ("max30102", max30102_leer),
        ("max30205", max30205_leer),
        ("dht22",    dht22_leer),
        ("ldr",      ldr_leer),
    ]:
        try:
            datos[nombre] = fn()
        except Exception as e:
            datos[nombre] = {"error": str(e)}
    return datos


# ════════════════════════════════════════════════════════════
#  CONSOLA
# ════════════════════════════════════════════════════════════
def imprimir(d):
    print("\n━━━  SENSORES  ━━━")
    mpu = d.get("mpu6050", {})
    if "error" not in mpu:
        print("  MPU6050   Accel X:{:6.3f}g Y:{:6.3f}g Z:{:6.3f}g".format(mpu['ax'], mpu['ay'], mpu['az']))
        print("            Gyro  X:{:6.2f}°/s Y:{:6.2f}°/s Z:{:6.2f}°/s".format(mpu['gx'], mpu['gy'], mpu['gz']))
    else:
        print("  MPU6050   ERROR: {}".format(mpu['error']))

    hr = d.get("max30102", {})
    if "error" not in hr:
        print("  MAX30102  Rojo:{}  IR:{}".format(hr['rojo_raw'], hr['ir_raw']))
    else:
        print("  MAX30102  ERROR: {}".format(hr['error']))

    tc = d.get("max30205", {})
    if "error" not in tc:
        print("  MAX30205  Temp corporal: {} °C".format(tc['temp_corporal_C']))
    else:
        print("  MAX30205  ERROR: {}".format(tc['error']))

    dht_d = d.get("dht22", {})
    if "error" not in dht_d:
        print("  DHT22     Temp: {} °C  Humedad: {} %".format(dht_d['temp_ambiente_C'], dht_d['humedad_pct']))
    else:
        print("  DHT22     ERROR: {}".format(dht_d['error']))

    ldr_d = d.get("ldr", {})
    if "error" not in ldr_d:
        print("  LDR       {} ADC ({}%)".format(ldr_d['raw'], ldr_d['luz_pct']))
    else:
        print("  LDR       ERROR: {}".format(ldr_d['error']))
    print("─" * 40)


# ════════════════════════════════════════════════════════════
#  ARRANQUE
# ════════════════════════════════════════════════════════════
print("=" * 40)
print("  ESP32-C3 | IoT Sensores via WSS")
print("=" * 40)

found = i2c.scan()
print("I2C detectados:", [hex(x) for x in found])

mpu6050_init()
max30102_init()
print("Sensores iniciados OK")

wlan = conectar_wifi()
if wlan:
    conectar_mqtt()
else:
    print("Sin Wi-Fi — solo consola")

print("Loop cada {}s\n".format(INTERVALO_SEG))


# ════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ════════════════════════════════════════════════════════════
while True:
    # Reconectar WiFi si se cayó
    if not wlan or not wlan.isconnected():
        print("  WiFi caido — reconectando...")
        wlan = conectar_wifi()
        if wlan and not mqtt_client:
            conectar_mqtt()

    datos = leer_todos()
    imprimir(datos)

    if mqtt_client:
        publicar(datos)
    else:
        print("  (sin MQTT — solo consola)")

    time.sleep(INTERVALO_SEG)