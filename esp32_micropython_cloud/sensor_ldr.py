# sensor_ldr.py - Módulo para LDR
import machine
import time
import config

class SensorLDR:
    def __init__(self):
        self.adc = machine.ADC(machine.Pin(config.LDR_PIN))
        # Rango completo: 0 (oscuridad) a 4095 (luz directa)
        self.adc.atten(machine.ADC.ATTN_11DB)
        self.adc.width(machine.ADC.WIDTH_12BIT)
        self.ultima_lectura = 0
        self.intervalo = config.LDR_INTERVAL
        self.nombre = "ldr"

    def leer_y_publicar(self, mqtt_client, device_id):
        ahora = time.time()
        if ahora - self.ultima_lectura < self.intervalo:
            return False

        try:
            # Promedio de 10 muestras para estabilizar
            suma = 0
            for _ in range(10):
                suma += self.adc.read()
                time.sleep_ms(5)
            valor = suma // 10

            # Normalizar a porcentaje (0-100)
            # Nota: el LDR da valores INVERTIDOS (más luz = menos resistencia = menos voltaje)
            # Ajustá si ves que va al revés en tu circuito
            porcentaje = int((valor / 4095) * 100)

            topic = "sensores/{}/luz".format(device_id)
            mqtt_client.publish(topic, porcentaje)

            print("  [LDR] Luz: {}% (raw: {})".format(porcentaje, valor))
            self.ultima_lectura = ahora
            return True
        except Exception as e:
            print("  [LDR] Error:", e)
            return False