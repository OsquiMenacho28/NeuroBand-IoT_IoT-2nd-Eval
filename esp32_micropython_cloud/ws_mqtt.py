# ws_mqtt.py - MQTT sobre WebSocket Secure minimalista para MicroPython
# Uso: cliente = MQTTWSClient(host, port, path, user, password, client_id)
#      cliente.connect()
#      cliente.publish(topic, payload)

import usocket as socket
import ssl as ssl
import ustruct as struct
import urandom as random
import ubinascii as binascii

class MQTTWSClient:
    def __init__(self, host, port, path, user, password, client_id):
        self.host = host
        self.port = port
        self.path = path
        self.user = user
        self.password = password
        self.client_id = client_id
        self.sock = None

    def _ws_handshake(self):
        # Genera key random de 16 bytes en base64
        key = binascii.b2a_base64(bytes([random.getrandbits(8) for _ in range(16)])).strip()
        req = (
            "GET {path} HTTP/1.1\r\n"
            "Host: {host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "Sec-WebSocket-Protocol: mqtt\r\n"
            "\r\n"
        ).format(path=self.path, host=self.host, key=key.decode())
        self.sock.write(req.encode())

        # Leer respuesta hasta \r\n\r\n
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.read(1)
            if not chunk:
                raise OSError("WebSocket handshake failed: sin respuesta")
            response += chunk

        if b"101" not in response.split(b"\r\n")[0]:
            raise OSError("WebSocket handshake failed: " + response.decode()[:100])

    def _ws_send(self, data):
        # Envía data como frame binario WebSocket con masking (requerido por cliente)
        frame = bytearray()
        frame.append(0x82)  # FIN=1, opcode=0x2 (binary)
        length = len(data)
        mask_key = bytes([random.getrandbits(8) for _ in range(4)])

        if length < 126:
            frame.append(0x80 | length)
        elif length < 65536:
            frame.append(0x80 | 126)
            frame.extend(struct.pack("!H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack("!Q", length))

        frame.extend(mask_key)
        masked = bytearray(length)
        for i in range(length):
            masked[i] = data[i] ^ mask_key[i % 4]
        frame.extend(masked)
        self.sock.write(frame)

    def _ws_recv(self):
        # Recibe un frame WS completo y devuelve el payload
        header = self.sock.read(2)
        if not header or len(header) < 2:
            raise OSError("Conexión cerrada")
        length = header[1] & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.sock.read(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.sock.read(8))[0]
        return self.sock.read(length)

    def connect(self):
        # 1. TCP
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        raw_sock = socket.socket()
        raw_sock.connect(addr)

        # 2. TLS (sin validar CA para simplificar - solo cifrado)
        self.sock = ssl.wrap_socket(raw_sock, server_hostname=self.host)

        # 3. WebSocket upgrade
        self._ws_handshake()

        # 4. MQTT CONNECT
        self._mqtt_connect()

    def _mqtt_connect(self):
        # Variable header: protocol name "MQTT" + level 4 + flags + keepalive
        proto = b"\x00\x04MQTT\x04"   # protocol "MQTT", level 4 (MQTT 3.1.1)
        flags = 0xC2  # username + password + clean session
        keepalive = struct.pack("!H", 60)

        # Payload: client_id + username + password
        payload = struct.pack("!H", len(self.client_id)) + self.client_id.encode()
        payload += struct.pack("!H", len(self.user)) + self.user.encode()
        payload += struct.pack("!H", len(self.password)) + self.password.encode()

        var_header = proto + bytes([flags]) + keepalive
        remaining = var_header + payload

        packet = bytes([0x10]) + self._encode_length(len(remaining)) + remaining
        self._ws_send(packet)

        # Leer CONNACK
        resp = self._ws_recv()
        if len(resp) < 4 or resp[0] != 0x20:
            raise OSError("MQTT CONNACK inválido")
        if resp[3] != 0x00:
            raise OSError("MQTT auth fallida, código: " + str(resp[3]))

    def publish(self, topic, payload):
        if isinstance(payload, (int, float)):
            payload = str(payload)
        if isinstance(payload, str):
            payload = payload.encode()

        var_header = struct.pack("!H", len(topic)) + topic.encode()
        remaining = var_header + payload

        packet = bytes([0x30]) + self._encode_length(len(remaining)) + remaining
        self._ws_send(packet)

    def disconnect(self):
        try:
            self._ws_send(bytes([0xE0, 0x00]))   # MQTT DISCONNECT
            self.sock.close()
        except:
            pass
        self.sock = None

    def ping(self):
        self._ws_send(bytes([0xC0, 0x00]))   # MQTT PINGREQ

    @staticmethod
    def _encode_length(length):
        # MQTT Variable Length Encoding
        result = bytearray()
        while True:
            byte = length % 128
            length //= 128
            if length > 0:
                byte |= 0x80
            result.append(byte)
            if length == 0:
                break
        return bytes(result)