# ============================================================
#  mqtt_ws.py — MQTT sobre WebSocket + SSL para MicroPython
#  Basado en la técnica de Christopher Cooper / Christian Becker
#  Compatible con ESP32-C3 MicroPython v1.20+
# ============================================================

try:
    import usocket as socket
except:
    import socket

try:
    import ussl as ssl
except:
    import ssl

import ubinascii
import os
from umqtt.simple import MQTTClient


class MQTTWebsocketClient(MQTTClient):
    """
    Extiende MQTTClient para conectarse a través de WebSocket (ws:// o wss://).
    Uso idéntico a MQTTClient, solo cambia la clase.
    """

    WS_PATH = "/mqtt"   # ruta del nginx

    def __create_websocket(self):
        # 1. Socket TCP normal
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)

        # 2. Envolver con SSL si corresponde
        if self.ssl:
            self.sock = ssl.wrap_socket(
                self.sock,
                server_hostname=self.server,
                **self.ssl_params
            )

        # 3. Handshake WebSocket
        key_bytes = ubinascii.b2a_base64(os.urandom(16)).strip()
        handshake = (
            "GET {path} HTTP/1.1\r\n"
            "Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Protocol: mqtt\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        ).format(
            path=self.WS_PATH,
            host=self.server,
            port=self.port,
            key=key_bytes.decode()
        )
        self.sock.write(handshake.encode())

        # 4. Leer respuesta HTTP hasta encontrar fin de headers
        while True:
            line = self.sock.readline()
            if line in (b"\r\n", b""):
                break

    def connect(self, clean_session=True):
        self.__create_websocket()
        # Llama al método interno de umqtt que hace el handshake MQTT
        # (sin volver a crear el socket)
        return self._MQTTClient__connect(clean_session)

    # ── Framing WebSocket ────────────────────────────────────
    # El broker espera frames WebSocket alrededor de los paquetes MQTT

    def _send_str(self, s):
        self.__ws_write(s)

    def write(self, data):
        self.__ws_write(data)

    def __ws_write(self, data):
        """Envuelve los bytes en un frame WebSocket binario (opcode 0x02)."""
        length = len(data)
        # Máscara aleatoria obligatoria en cliente→servidor
        mask = os.urandom(4)
        if length < 126:
            header = bytes([0x82, 0x80 | length]) + mask
        elif length < 65536:
            header = bytes([0x82, 0xFE,
                            (length >> 8) & 0xFF,
                             length & 0xFF]) + mask
        else:
            header = bytes([0x82, 0xFF,
                            0, 0, 0, 0,
                            (length >> 24) & 0xFF,
                            (length >> 16) & 0xFF,
                            (length >> 8)  & 0xFF,
                             length        & 0xFF]) + mask
        masked = bytes([data[i] ^ mask[i % 4] for i in range(length)])
        self.sock.write(header + masked)

    def read(self, n):
        """Lee n bytes de datos WebSocket desenmascarados."""
        # Leer header del frame
        b1 = self.sock.read(1)[0]
        b2 = self.sock.read(1)[0]
        masked = (b2 & 0x80) != 0
        length = b2 & 0x7F
        if length == 126:
            length = int.from_bytes(self.sock.read(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.sock.read(8), 'big')
        if masked:
            mask = self.sock.read(4)
        raw = self.sock.read(length)
        if masked:
            raw = bytes([raw[i] ^ mask[i % 4] for i in range(length)])
        # Devolver solo los n bytes pedidos
        return raw[:n]
