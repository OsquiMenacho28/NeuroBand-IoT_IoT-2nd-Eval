# main.py - ESP32-01 Ambiente (DHT22 + PIR + LDR)
import time
import network
import machine
import config
from ws_mqtt import MQTTWSClient

# LED onboard
led = machine.Pin(2, machine.Pin.OUT)

def blink(times=1, delay=0.1):
    for _ in range(times):
        led.value(1); time.sleep(delay)
        led.value(0); time.sleep(delay)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi:", config.WIFI_SSID)
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(1)
            print(".", end="")
        print()
    if wlan.isconnected():
        print("WiFi OK:", wlan.ifconfig()[0])
        blink(2, 0.1)
        return True
    return False

def conectar_mqtt():
    client = MQTTWSClient(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        path=config.MQTT_PATH,
        user=config.MQTT_USER,
        password=config.MQTT_PASSWORD,
        client_id=config.MQTT_CLIENT_ID,
    )
    client.connect()
    print("MQTT OK:", config.MQTT_HOST)
    blink(3, 0.1)
    return client

def cargar_sensores():
    sensores = []
    for nombre in config.SENSORES_ACTIVOS:
        try:
            if nombre == "dht":
                from sensor_dht import SensorDHT
                sensores.append(SensorDHT())
            elif nombre == "hcsr04":
                from sensor_hcsr04 import SensorHCSR04
                sensores.append(SensorHCSR04())
            elif nombre == "ldr":
                from sensor_ldr import SensorLDR
                sensores.append(SensorLDR())
            print("Sensor cargado:", nombre)
        except Exception as e:
            print("Error cargando sensor", nombre, ":", e)
    return sensores

def main():
    # WiFi
    if not conectar_wifi():
        print("WiFi falló, reiniciando en 10s...")
        time.sleep(10)
        machine.reset()

    # MQTT (con reintentos)
    client = None
    while client is None:
        try:
            client = conectar_mqtt()
        except Exception as e:
            print("Error MQTT:", e, "- reintentando en 5s")
            time.sleep(5)

    # Cargar sensores
    sensores = cargar_sensores()
    if not sensores:
        print("No hay sensores activos, nada que publicar")
        return

    print("\n==== Loop iniciado con", len(sensores), "sensores ====\n")
    errores_seguidos = 0

    while True:
        actividad = False

        for s in sensores:
            try:
                if s.leer_y_publicar(client, config.MQTT_CLIENT_ID):
                    actividad = True
                    errores_seguidos = 0
            except Exception as e:
                print("  [{}] Error publicando: {}".format(s.nombre, e))
                errores_seguidos += 1

        if actividad:
            blink(1, 0.02)

        # Si hay muchos errores seguidos, reconectar MQTT
        if errores_seguidos >= 5:
            print("Demasiados errores, reconectando MQTT...")
            try:
                client.disconnect()
            except:
                pass
            time.sleep(3)
            try:
                client = conectar_mqtt()
                errores_seguidos = 0
            except Exception as e:
                print("Reconexión falló:", e)
                time.sleep(10)

        # PIR necesita polling rápido para no perder eventos
        # Los otros sensores tienen su propio intervalo interno
        time.sleep_ms(200)

main()