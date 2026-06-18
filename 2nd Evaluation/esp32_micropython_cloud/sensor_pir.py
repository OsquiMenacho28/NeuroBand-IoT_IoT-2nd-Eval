# sensor_pir.py - Módulo para PIR HC-SR505
import machine
import config

class SensorPIR:
    def __init__(self):
        self.pin = machine.Pin(config.PIR_PIN, machine.Pin.IN)
        self.ultimo_estado = self.pin.value()
        self.nombre = "pir"

    def leer_y_publicar(self, mqtt_client, device_id):
        estado_actual = self.pin.value()

        # Solo publicar si cambió el estado
        if estado_actual != self.ultimo_estado:
            topic = "sensores/{}/movimiento".format(device_id)
            mqtt_client.publish(topic, estado_actual)
            if estado_actual == 1:
                print("  [PIR] ⚡ MOVIMIENTO detectado")
            else:
                print("  [PIR] ✓ Quieto")
            self.ultimo_estado = estado_actual
            return True
        return False