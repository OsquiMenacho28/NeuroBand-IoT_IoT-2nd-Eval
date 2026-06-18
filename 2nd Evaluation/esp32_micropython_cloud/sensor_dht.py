# sensor_dht.py - Módulo para DHT22
import dht
import machine
import time
import config

class SensorDHT:
    def __init__(self):
        self.sensor = dht.DHT22(machine.Pin(config.DHT_PIN))
        self.ultima_lectura = 0
        self.intervalo = config.DHT_INTERVAL
        self.nombre = "dht"

    def leer_y_publicar(self, mqtt_client, device_id):
        # Solo publica si pasó el intervalo
        ahora = time.time()
        if ahora - self.ultima_lectura < self.intervalo:
            return False

        try:
            self.sensor.measure()
            temp = self.sensor.temperature()
            hum = self.sensor.humidity()

            topic_t = "sensores/{}/temperatura".format(device_id)
            topic_h = "sensores/{}/humedad".format(device_id)
            mqtt_client.publish(topic_t, temp)
            mqtt_client.publish(topic_h, hum)

            print("  [DHT] T={}°C  H={}%".format(temp, hum))
            self.ultima_lectura = ahora
            return True
        except Exception as e:
            print("  [DHT] Error:", e)
            return False