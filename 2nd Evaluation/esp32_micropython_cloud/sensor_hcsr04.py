# sensor_hcsr04.py - Módulo para HC-SR04 (sensor ultrasónico de distancia)
import machine
import time
import config

class SensorHCSR04:
    def __init__(self):
        self.trig = machine.Pin(config.HCSR04_TRIG_PIN, machine.Pin.OUT)
        self.echo = machine.Pin(config.HCSR04_ECHO_PIN, machine.Pin.IN)
        self.trig.value(0)
        self.ultima_lectura = 0
        self.intervalo = config.HCSR04_INTERVAL
        self.nombre = "hcsr04"
        # Esperar estabilización
        time.sleep_ms(50)

    def _medir_distancia_cm(self):
        """Hace una medición. Devuelve cm o None si timeout."""
        # Pulso de 10us en TRIG
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

        # Medir tiempo de ECHO en alto (timeout 30ms = ~5m máx)
        try:
            duracion_us = machine.time_pulse_us(self.echo, 1, 30000)
        except OSError:
            return None

        if duracion_us < 0:
            return None

        # Velocidad del sonido: 343 m/s = 0.0343 cm/us
        # Distancia = (tiempo * velocidad) / 2 (ida y vuelta)
        distancia = (duracion_us * 0.0343) / 2
        return distancia

    def leer_y_publicar(self, mqtt_client, device_id):
        ahora = time.time()
        if ahora - self.ultima_lectura < self.intervalo:
            return False

        try:
            # Promedio de 5 mediciones para estabilizar
            lecturas = []
            for _ in range(5):
                d = self._medir_distancia_cm()
                if d is not None and 2 <= d <= 400:
                    lecturas.append(d)
                time.sleep_ms(60)   # mínimo entre pulsos

            if not lecturas:
                print("  [HCSR04] Sin lecturas válidas")
                return False

            # Mediana para descartar outliers
            lecturas.sort()
            distancia = round(lecturas[len(lecturas) // 2], 1)

            topic = "sensores/{}/distancia".format(device_id)
            mqtt_client.publish(topic, distancia)

            print("  [HCSR04] Distancia: {} cm".format(distancia))
            self.ultima_lectura = ahora
            return True
        except Exception as e:
            print("  [HCSR04] Error:", e)
            return False