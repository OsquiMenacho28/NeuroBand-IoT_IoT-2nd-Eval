# NeuroBand IoT — Sleep Quality Monitoring System

> **Course:** Internet of Things — 2nd Evaluation  
> **Team:** The IoT Architects  
> **Spring Boot package:** `com.TheIoTArchitects.IoT2Eval`

---

## Project Overview

NeuroBand IoT is a wearable sleep monitoring band that collects biometric data from 3 sensors on an **ESP32** running **MicroPython**, sends it to a **Spring Boot** backend via REST API, stores it in **Supabase (PostgreSQL)**, and visualizes everything in real-time on a **Vue 3 + Vite** dashboard with threshold-based alerts.

---

## Architecture

```
  [ESP32 — MicroPython]
       │
       │  HTTP POST (WiFi, same LAN or internet)
       ▼
  [Spring Boot :8080]  ──── Supabase PostgreSQL (cloud)
       │
       │  SSE (Server-Sent Events)
       ▼
  [Vue Dashboard :5173]
```

---

## Sensors & Sleep Thresholds

### MPU6050 — Accelerometer & Gyroscope (Motion)

Detects body movement to classify sleep restlessness.

| Threshold | Range        | Status   | Meaning                 |
| --------- | ------------ | -------- | ----------------------- |
| STILL     | mag < 0.15 g | 🟢 Good  | Deep sleep, no movement |
| LIGHT     | 0.15–0.50 g  | 🟡 Warn  | REM phase / light sleep |
| ACTIVE    | > 0.50 g     | 🔴 Alert | Restless / awake        |

### MAX30102 — Heart Rate & SpO₂ (Optical)

Monitors heart rate and blood oxygen saturation.

**Heart Rate:**
| Threshold | Range | Status |
|-----------|-------|--------|
| DEEP_SLEEP | 40–60 bpm | 🟢 Ideal for recovery |
| RESTING | 60–80 bpm | 🟡 Light sleep |
| AWAKE | > 80 bpm | 🔴 Alert |

**SpO₂:**
| Threshold | Range | Status |
|-----------|-------|--------|
| HEALTHY | ≥ 95% | 🟢 Normal |
| MILD_HYPOXIA | 90–94% | 🟡 Monitor |
| CRITICAL | < 90% | 🔴 Alert |

### LDR — Ambient Light (Melatonin)

Light exposure directly affects melatonin production and sleep quality.

| Threshold | Range | Status                   |
| --------- | ----- | ------------------------ |
| IDEAL     | < 5%  | 🟢 Optimal for melatonin |
| DIM       | 5–30% | 🟡 Acceptable            |
| BRIGHT    | > 30% | 🔴 Suppresses melatonin  |

---

## Project Structure

```
neuroband/
│
├── .gitignore
├── README.md
│
├── database/
│   └── schema.sql              ← Run this in Supabase SQL Editor
│
├── backend/                    ← Spring Boot (com.TheIoTArchitects.IoT2Eval)
│   ├── .env                    ← ⚠️ NOT in git — fill your Supabase credentials
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/TheIoTArchitects/IoT2Eval/
│       │   ├── NeuroBandApplication.java
│       │   ├── config/CorsConfig.java
│       │   ├── controller/SensorController.java
│       │   ├── model/
│       │   │   ├── Mpu6050Reading.java
│       │   │   ├── Max30102Reading.java
│       │   │   ├── LdrReading.java
│       │   │   └── Dtos.java
│       │   ├── repository/
│       │   │   ├── Mpu6050Repository.java
│       │   │   ├── Max30102Repository.java
│       │   │   └── LdrRepository.java
│       │   └── service/
│       │       ├── ThresholdEvaluator.java
│       │       ├── SensorService.java
│       │       └── SseService.java
│       └── resources/
│           └── application.properties
│
├── frontend/                   ← Vue 3 + Vite dashboard
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue             ← Sidebar + sleep score ring
│       ├── assets/main.css
│       ├── router/index.js
│       ├── stores/neuroBandStore.js   ← Pinia + SSE
│       ├── components/
│       │   └── SensorChart.vue        ← Reusable chart with threshold bands
│       └── views/
│           ├── DashboardView.vue      ← Overview + sleep quality banner
│           ├── MovimientoView.vue     ← MPU6050 full detail
│           ├── CorazonView.vue        ← MAX30102 HR + SpO2
│           ├── LuzView.vue            ← LDR + melatonin science
│           └── TablaView.vue          ← All data tables
│
└── esp32_micropython/          ← Flash these files to the ESP32
    ├── config.py               ← ⚠️ NOT in git — WiFi + server credentials
    ├── wifi.py                 ← WiFi connection manager
    ├── mpu6050.py              ← MPU6050 I2C driver
    ├── max30102.py             ← MAX30102 I2C driver + SpO2 algorithm
    ├── ldr.py                  ← LDR ADC driver
    ├── http_client.py          ← HTTP POST to Spring Boot
    └── main.py                 ← Entry point — boot, init, sensor loop
```

---

## Setup Guide

### 1. Supabase Database

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run `database/schema.sql`
3. Copy your **DB connection string** from Settings → Database

### 2. Backend — Spring Boot

Fill in `backend/.env` with your Supabase credentials:

```env
DB_URL=jdbc:postgresql://db.YOUR_PROJECT_REF.supabase.co:5432/postgres
DB_USERNAME=postgres
DB_PASSWORD=your_supabase_db_password
CORS_ORIGINS=http://localhost:5173
```

Load env vars and run:

```bash
# Linux/Mac
export $(cat backend/.env | xargs)

# Windows PowerShell
Get-Content backend/.env | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v) }

cd backend
mvn spring-boot:run
# → http://localhost:8080
```

### 3. Frontend — Vue Dashboard

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 4. ESP32 — MicroPython

**Edit `esp32_micropython/config.py`:**

```python
DEVICE_ID     = "neuroband_esp32_01"   # your device name
WIFI_SSID     = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"
SERVER_HOST   = "192.168.X.X"          # server LAN IP (run: ipconfig / ip a)
SERVER_PORT   = 8080
```

**Flash all files using Thonny IDE or mpremote:**

```bash
# Using mpremote (pip install mpremote)
mpremote connect /dev/ttyUSB0 cp config.py :config.py
mpremote connect /dev/ttyUSB0 cp wifi.py :wifi.py
mpremote connect /dev/ttyUSB0 cp mpu6050.py :mpu6050.py
mpremote connect /dev/ttyUSB0 cp max30102.py :max30102.py
mpremote connect /dev/ttyUSB0 cp ldr.py :ldr.py
mpremote connect /dev/ttyUSB0 cp http_client.py :http_client.py
mpremote connect /dev/ttyUSB0 cp main.py :main.py

# Run immediately
mpremote connect /dev/ttyUSB0 run main.py
```

**Or in Thonny:** Open each file → Save to MicroPython device.

---

## ESP32 Wiring

```
ESP32 Pin    Sensor         Signal
─────────────────────────────────────────
GPIO21       MPU6050        SDA  (I2C)
GPIO22       MPU6050        SCL  (I2C)
GPIO21       MAX30102       SDA  (shared I2C)
GPIO22       MAX30102       SCL  (shared I2C)
GPIO34       LDR            ADC  (analog in)
3.3V         All sensors    VCC
GND          All sensors    GND

LDR voltage divider:
  3.3V → 10kΩ → GPIO34 → LDR → GND

I2C Addresses:
  MPU6050:  0x68
  MAX30102: 0x57
```

---

## REST API Endpoints

| Method | Endpoint        | Description                  |
| ------ | --------------- | ---------------------------- |
| GET    | `/api/status`   | Health check                 |
| GET    | `/api/stream`   | SSE stream for Vue dashboard |
| POST   | `/api/mpu6050`  | Insert MPU6050 reading       |
| GET    | `/api/mpu6050`  | Get all MPU6050 readings     |
| POST   | `/api/max30102` | Insert MAX30102 reading      |
| GET    | `/api/max30102` | Get all MAX30102 readings    |
| POST   | `/api/ldr`      | Insert LDR reading           |
| GET    | `/api/ldr`      | Get all LDR readings         |

### Example POST /api/mpu6050

```json
{
  "deviceId": "neuroband_esp32_01",
  "accelX": 0.02,
  "accelY": -0.01,
  "accelZ": 0.98,
  "gyroX": 0.5,
  "gyroY": -0.3,
  "gyroZ": 0.1
}
```

### Example POST /api/ldr

```json
{
  "deviceId": "neuroband_esp32_01",
  "luxPercent": 3.5,
  "voltage": 0.115
}
```

---

## Technologies

| Layer             | Technology                                              |
| ----------------- | ------------------------------------------------------- |
| Microcontroller   | ESP32 + MicroPython                                     |
| Backend           | Java 17, Spring Boot 3.2, Spring Data JPA               |
| Database          | PostgreSQL via Supabase (cloud)                         |
| Real-time         | Server-Sent Events (SSE)                                |
| Frontend          | Vue 3, Vite, Pinia, Vue Router, Chart.js 4, vue-chartjs |
| Fonts             | Syne (display) + DM Mono (data)                         |
| Secret management | .env (gitignored)                                       |
