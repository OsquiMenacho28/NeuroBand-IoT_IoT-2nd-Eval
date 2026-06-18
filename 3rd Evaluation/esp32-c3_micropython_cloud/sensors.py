# ============================================================
#  sensors.py — ESP32-C3 Mini  |  MicroPython
#  Lee: MPU6050, MAX30102, MAX30205, DHT22, LDR
#  Imprime todos los datos por consola (paso previo al MQTT)
# ============================================================

import time
import machine
from machine import Pin, ADC, SoftI2C
import dht

# ── Pines ────────────────────────────────────────────────────
I2C_SDA  = 8      # G8
I2C_SCL  = 9      # G9
DHT_PIN  = 10     # G10
LDR_PIN  = 2      # G2  (AO — analógico)

# ── Bus I2C compartido ───────────────────────────────────────
i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

# ── DHT22 ────────────────────────────────────────────────────
sensor_dht = dht.DHT22(Pin(DHT_PIN))

# ── LDR (ADC) ────────────────────────────────────────────────
ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)   # rango 0–3.3 V

# ════════════════════════════════════════════════════════════
#  MPU6050 (0x68)
# ════════════════════════════════════════════════════════════
MPU_ADDR = 0x68

def mpu6050_init():
    # Saca el chip del modo sleep (registro PWR_MGMT_1 = 0x6B)
    i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
    time.sleep_ms(100)

def mpu6050_leer():
    """Devuelve dict con accel (g) y gyro (°/s)."""
    # Lectura de 14 bytes desde registro 0x3B
    data = i2c.readfrom_mem(MPU_ADDR, 0x3B, 14)
    def to_signed(h, l):
        v = (h << 8) | l
        return v - 65536 if v >= 32768 else v

    ax = to_signed(data[0],  data[1])  / 16384.0   # ±2g
    ay = to_signed(data[2],  data[3])  / 16384.0
    az = to_signed(data[4],  data[5])  / 16384.0
    gx = to_signed(data[8],  data[9])  / 131.0     # ±250°/s
    gy = to_signed(data[10], data[11]) / 131.0
    gz = to_signed(data[12], data[13]) / 131.0

    return {"ax": round(ax,3), "ay": round(ay,3), "az": round(az,3),
            "gx": round(gx,2), "gy": round(gy,2), "gz": round(gz,2)}

# ════════════════════════════════════════════════════════════
#  MAX30102 (0x57)  — Pulso y SpO2
# ════════════════════════════════════════════════════════════
MAX30102_ADDR = 0x57

def max30102_init():
    # Reset
    i2c.writeto_mem(MAX30102_ADDR, 0x09, b'\x40')
    time.sleep_ms(100)
    # FIFO config
    i2c.writeto_mem(MAX30102_ADDR, 0x08, b'\x4F')  # FIFO_CONFIG
    # Modo SpO2 (0x03) — habilita LED rojo + IR
    i2c.writeto_mem(MAX30102_ADDR, 0x09, b'\x03')
    # SpO2 config: ADC 4096nA, 100 samples/s, 411µs pulso
    i2c.writeto_mem(MAX30102_ADDR, 0x0A, b'\x27')
    # Amplitud LED1 (rojo) y LED2 (IR) al ~10 mA
    i2c.writeto_mem(MAX30102_ADDR, 0x0C, b'\x24')
    i2c.writeto_mem(MAX30102_ADDR, 0x0D, b'\x24')

def max30102_leer_raw():
    """Lee un sample crudo del FIFO. Devuelve (rojo, ir)."""
    # Leer punteros FIFO
    wr  = i2c.readfrom_mem(MAX30102_ADDR, 0x04, 1)[0] & 0x1F
    rd  = i2c.readfrom_mem(MAX30102_ADDR, 0x06, 1)[0] & 0x1F
    if wr == rd:
        return None, None   # FIFO vacío

    data = i2c.readfrom_mem(MAX30102_ADDR, 0x07, 6)
    rojo = ((data[0] & 0x03) << 16) | (data[1] << 8) | data[2]
    ir   = ((data[3] & 0x03) << 16) | (data[4] << 8) | data[5]
    return rojo, ir

# ════════════════════════════════════════════════════════════
#  MAX30205 (0x4c)  — Temperatura corporal
# ════════════════════════════════════════════════════════════
MAX30205_ADDR = 0x4c

def max30205_leer():
    """Devuelve temperatura en °C."""
    data = i2c.readfrom_mem(MAX30205_ADDR, 0x00, 2)
    raw = (data[0] << 8) | data[1]
    if raw >= 32768:
        raw -= 65536
    return round(raw * 0.00390625, 2)   # LSB = 1/256 °C

# ════════════════════════════════════════════════════════════
#  LDR — Luminosidad
# ════════════════════════════════════════════════════════════
def ldr_leer():
    """Devuelve valor ADC (0–4095) y porcentaje de luz (0–100%)."""
    raw = ldr.read()
    pct = round((raw / 4095) * 100, 1)
    return raw, pct

# ════════════════════════════════════════════════════════════
#  INICIALIZACIÓN
# ════════════════════════════════════════════════════════════
def inicializar():
    print("Iniciando sensores...")
    # Verificar dispositivos I2C
    dispositivos = i2c.scan()
    print("  I2C encontrados:", [hex(d) for d in dispositivos])

    esperados = [MPU_ADDR, MAX30102_ADDR, MAX30205_ADDR]
    for addr in esperados:
        if addr not in dispositivos:
            print(f"  ⚠️  Sensor {hex(addr)} NO detectado — revisá el cableado")

    mpu6050_init()
    print("  MPU6050  OK")
    max30102_init()
    print("  MAX30102 OK")
    print("  MAX30205 OK (no requiere init)")
    print("  DHT22    OK")
    print("  LDR      OK")
    print("─" * 50)

# ════════════════════════════════════════════════════════════
#  LECTURA COMPLETA
# ════════════════════════════════════════════════════════════
def leer_todos():
    datos = {}

    # — MPU6050 —
    try:
        mpu = mpu6050_leer()
        datos["mpu6050"] = mpu
    except Exception as e:
        datos["mpu6050"] = {"error": str(e)}

    # — MAX30102 —
    try:
        rojo, ir = max30102_leer_raw()
        datos["max30102"] = {"rojo_raw": rojo, "ir_raw": ir}
    except Exception as e:
        datos["max30102"] = {"error": str(e)}

    # — MAX30205 —
    try:
        temp_corp = max30205_leer()
        datos["max30205"] = {"temp_corporal_C": temp_corp}
    except Exception as e:
        datos["max30205"] = {"error": str(e)}

    # — DHT22 —
    try:
        sensor_dht.measure()
        datos["dht22"] = {
            "temp_C":   sensor_dht.temperature(),
            "humedad_pct": sensor_dht.humidity()
        }
    except Exception as e:
        datos["dht22"] = {"error": str(e)}

    # — LDR —
    try:
        raw, pct = ldr_leer()
        datos["ldr"] = {"raw": raw, "luz_pct": pct}
    except Exception as e:
        datos["ldr"] = {"error": str(e)}

    return datos

# ════════════════════════════════════════════════════════════
#  IMPRIMIR FORMATO LEGIBLE
# ════════════════════════════════════════════════════════════
def imprimir(datos):
    print("\n━━━  LECTURA DE SENSORES  ━━━")

    mpu = datos.get("mpu6050", {})
    if "error" not in mpu:
        print(f"  [MPU6050]  Accel → X:{mpu['ax']:6.3f}g  Y:{mpu['ay']:6.3f}g  Z:{mpu['az']:6.3f}g")
        print(f"             Gyro  → X:{mpu['gx']:7.2f}°/s  Y:{mpu['gy']:7.2f}°/s  Z:{mpu['gz']:7.2f}°/s")
    else:
        print(f"  [MPU6050]  ERROR: {mpu['error']}")

    hr = datos.get("max30102", {})
    if "error" not in hr:
        print(f"  [MAX30102] Rojo RAW: {hr['rojo_raw']}  |  IR RAW: {hr['ir_raw']}")
        print( "             (procesá estos valores con algoritmo de BPM/SpO2)")
    else:
        print(f"  [MAX30102] ERROR: {hr['error']}")

    tc = datos.get("max30205", {})
    if "error" not in tc:
        print(f"  [MAX30205] Temp corporal: {tc['temp_corporal_C']} °C")
    else:
        print(f"  [MAX30205] ERROR: {tc['error']}")

    dht = datos.get("dht22", {})
    if "error" not in dht:
        print(f"  [DHT22]    Temp ambiente: {dht['temp_C']} °C  |  Humedad: {dht['humedad_pct']} %")
    else:
        print(f"  [DHT22]    ERROR: {dht['error']}")

    ldr = datos.get("ldr", {})
    if "error" not in ldr:
        print(f"  [LDR]      Luminosidad:  {ldr['raw']} ADC  ({ldr['luz_pct']}%)")
    else:
        print(f"  [LDR]      ERROR: {ldr['error']}")

    print("─" * 50)

# ════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ════════════════════════════════════════════════════════════
inicializar()

INTERVALO_SEG = 1   # ← cambiá este valor para ajustar la frecuencia

while True:
    datos = leer_todos()
    imprimir(datos)
    time.sleep(INTERVALO_SEG)
