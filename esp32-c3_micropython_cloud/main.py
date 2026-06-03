# ============================================================
#  main.py — ESP32-C3 Mini  |  MicroPython
#  Lee todos los sensores y publica por MQTT a Mosquitto
#  Broker: 10.1.232.20:1883
#  Topic:  proyecto/esp32_01/sensores
# ============================================================

import time
import json
import network
import machine
from machine import Pin, ADC, SoftI2C
import dht
from umqtt.simple import MQTTClient

# ── Configuración WiFi ───────────────────────────────────────
WIFI_SSID     = "SSID_AQUI"
WIFI_PASS     = "PASSWORD_AQUI"

# ── Configuración MQTT ───────────────────────────────────────
MQTT_BROKER   = "10.1.232.20"
MQTT_PORT     = 1883
MQTT_USER     = "esp32user"
MQTT_PASS     = "tprp1106"
MQTT_TOPIC    = b"proyecto/esp32_01/sensores"
MQTT_CLIENT   = "esp32_01"

# ── Pines ────────────────────────────────────────────────────
I2C_SDA  = 8
I2C_SCL  = 9
DHT_PIN  = 10
LDR_PIN  = 2

# ── Bus I2C ──────────────────────────────────────────────────
i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

# ── DHT22 ────────────────────────────────────────────────────
sensor_dht = dht.DHT22(Pin(DHT_PIN))

# ── LDR ──────────────────────────────────────────────────────
ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)

# ── Direcciones I2C ──────────────────────────────────────────
MPU_ADDR      = 0x68
MAX30102_ADDR = 0x57
MAX30205_ADDR = 0x4c

# ── Intervalo de publicación ─────────────────────────────────
INTERVALO_SEG = 1


# ════════════════════════════════════════════════════════════
#  WIFI
# ════════════════════════════════════════════════════════════
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    if wlan.isconnected():
        print("  WiFi ya conectado:", wlan.ifconfig()[0])
        return wlan
    print(f"  Conectando a '{WIFI_SSID}'", end="")
    wlan.connect(WIFI_SSID, WIFI_PASS)
    intentos = 0
    while not wlan.isconnected():
        time.sleep(1)
        print(".", end="")
        intentos += 1
        if intentos > 20:
            print("\n  ✗ No se pudo conectar al WiFi")
            return None
    print(f"\n  ✓ WiFi conectado — IP: {wlan.ifconfig()[0]}")
    return wlan


# ════════════════════════════════════════════════════════════
#  MQTT
# ════════════════════════════════════════════════════════════
mqtt_client = None

def conectar_mqtt():
    global mqtt_client
    try:
        client = MQTTClient(
            MQTT_CLIENT,
            MQTT_BROKER,
            port=MQTT_PORT,
            user=MQTT_USER,
            password=MQTT_PASS,
            keepalive=60
        )
        client.connect()
        mqtt_client = client
        print(f"  ✓ MQTT conectado a {MQTT_BROKER}:{MQTT_PORT}")
        return client
    except Exception as e:
        print(f"  ✗ MQTT error: {e}")
        return None

def publicar(payload_dict):
    global mqtt_client
    try:
        msg = json.dumps(payload_dict)
        mqtt_client.publish(MQTT_TOPIC, msg.encode())
        print(f"  ✓ Publicado ({len(msg)} bytes)")
        return True
    except Exception as e:
        print(f"  ✗ Error al publicar: {e} — reconectando MQTT...")
        mqtt_client = None
        conectar_mqtt()
        return False


# ════════════════════════════════════════════════════════════
#  SENSORES
# ════════════════════════════════════════════════════════════

# ── MPU6050 ──────────────────────────────────────────────────
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

# ── MAX30102 ─────────────────────────────────────────────────
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

# ── MAX30205 ─────────────────────────────────────────────────
def max30205_leer():
    data = i2c.readfrom_mem(MAX30205_ADDR, 0x00, 2)
    raw = (data[0] << 8) | data[1]
    if raw >= 32768:
        raw -= 65536
    return {"temp_corporal_C": round(raw * 0.00390625, 2)}

# ── DHT22 ────────────────────────────────────────────────────
def dht22_leer():
    sensor_dht.measure()
    return {
        "temp_ambiente_C": sensor_dht.temperature(),
        "humedad_pct":     sensor_dht.humidity()
    }

# ── LDR ──────────────────────────────────────────────────────
def ldr_leer():
    raw = ldr.read()
    return {
        "raw":     raw,
        "luz_pct": round((raw / 4095) * 100, 1)
    }

# ── Lectura completa ─────────────────────────────────────────
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
#  IMPRIMIR CONSOLA
# ════════════════════════════════════════════════════════════
def imprimir(d):
    print("\n━━━  SENSORES  ━━━")
    mpu = d.get("mpu6050", {})
    if "error" not in mpu:
        print(f"  MPU6050   Accel X:{mpu['ax']:6.3f}g Y:{mpu['ay']:6.3f}g Z:{mpu['az']:6.3f}g")
        print(f"            Gyro  X:{mpu['gx']:6.2f}°/s Y:{mpu['gy']:6.2f}°/s Z:{mpu['gz']:6.2f}°/s")
    else:
        print(f"  MPU6050   ERROR: {mpu['error']}")

    hr = d.get("max30102", {})
    if "error" not in hr:
        print(f"  MAX30102  Rojo:{hr['rojo_raw']}  IR:{hr['ir_raw']}")
    else:
        print(f"  MAX30102  ERROR: {hr['error']}")

    tc = d.get("max30205", {})
    if "error" not in tc:
        print(f"  MAX30205  Temp corporal: {tc['temp_corporal_C']} °C")
    else:
        print(f"  MAX30205  ERROR: {tc['error']}")

    dht = d.get("dht22", {})
    if "error" not in dht:
        print(f"  DHT22     Temp: {dht['temp_ambiente_C']} °C  Humedad: {dht['humedad_pct']} %")
    else:
        print(f"  DHT22     ERROR: {dht['error']}")

    ldr_d = d.get("ldr", {})
    if "error" not in ldr_d:
        print(f"  LDR       {ldr_d['raw']} ADC ({ldr_d['luz_pct']}%)")
    else:
        print(f"  LDR       ERROR: {ldr_d['error']}")
    print("─" * 40)


# ════════════════════════════════════════════════════════════
#  ARRANQUE
# ════════════════════════════════════════════════════════════
print("=" * 40)
print("  ESP32-C3 | IoT Sensores")
print("=" * 40)

# I2C scan
found = i2c.scan()
print("I2C detectados:", [hex(x) for x in found])

# Init sensores I2C
mpu6050_init()
max30102_init()
print("Sensores iniciados OK")

# WiFi
wlan = conectar_wifi()
if not wlan:
    print("Sin WiFi — publicando solo por consola")

# MQTT
if wlan:
    conectar_mqtt()

print("Iniciando loop cada", INTERVALO_SEG, "seg...\n")


# ════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ════════════════════════════════════════════════════════════
while True:
    datos = leer_todos()
    imprimir(datos)

    if mqtt_client:
        publicar(datos)
    else:
        print("  (sin MQTT — solo consola)")

    time.sleep(INTERVALO_SEG)
