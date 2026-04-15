-- ============================================================
--  NeuroBand IoT — PostgreSQL Schema
--  Project: Sleep Quality & Wellness Monitoring Band
--  Sensors: MPU6050 (motion), MAX30102 (heart rate/SpO2), LDR (light)
--  DB: Supabase (PostgreSQL in the cloud)
-- ============================================================

-- NOTE: Run this in Supabase SQL Editor or psql against your Supabase project.
-- Replace the connection string in application.properties accordingly.

-- ── Table 1: MPU6050 — Accelerometer & Gyroscope (6-axis motion) ─────────
-- Purpose: Detect body movement, sleep position, and restlessness during sleep.
-- Sleep thresholds:
--   acceleration_magnitude < 0.15 g  → deep/still sleep
--   0.15 – 0.50 g                    → light movement (REM phase)
--   > 0.50 g                         → active movement / awake
CREATE TABLE mpu6050_readings (
    id                   BIGSERIAL PRIMARY KEY,
    accel_x              DOUBLE PRECISION NOT NULL,   -- g-force X axis
    accel_y              DOUBLE PRECISION NOT NULL,   -- g-force Y axis
    accel_z              DOUBLE PRECISION NOT NULL,   -- g-force Z axis
    gyro_x               DOUBLE PRECISION NOT NULL,   -- °/s X axis
    gyro_y               DOUBLE PRECISION NOT NULL,   -- °/s Y axis
    gyro_z               DOUBLE PRECISION NOT NULL,   -- °/s Z axis
    accel_magnitude      DOUBLE PRECISION NOT NULL,   -- sqrt(x²+y²+z²) in g
    movement_level       VARCHAR(20)  NOT NULL,       -- 'STILL' | 'LIGHT' | 'ACTIVE'
    recorded_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    device_id            VARCHAR(60)  NOT NULL        -- ESP32 device identifier
);

-- ── Table 2: MAX30102 — Heart Rate & SpO2 ────────────────────────────────
-- Purpose: Monitor heart rate and blood oxygen saturation during sleep.
-- Sleep thresholds:
--   heart_rate: 40–60 bpm  → deep sleep (bradycardia, normal)
--               60–80 bpm  → light sleep / resting
--               > 80 bpm   → awake or stressed
--   spo2:       ≥ 95%      → healthy oxygen level
--               90–94%     → mild hypoxia — alert
--               < 90%      → severe hypoxia — critical alert
CREATE TABLE max30102_readings (
    id           BIGSERIAL PRIMARY KEY,
    heart_rate   DOUBLE PRECISION NOT NULL,   -- beats per minute (bpm)
    spo2         DOUBLE PRECISION NOT NULL,   -- blood oxygen % (SpO2)
    ir_value     BIGINT          NOT NULL,    -- raw infrared LED value
    red_value    BIGINT          NOT NULL,    -- raw red LED value
    hr_status    VARCHAR(20)     NOT NULL,    -- 'DEEP_SLEEP' | 'RESTING' | 'AWAKE'
    spo2_status  VARCHAR(20)     NOT NULL,    -- 'HEALTHY' | 'MILD_HYPOXIA' | 'CRITICAL'
    recorded_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    device_id    VARCHAR(60)     NOT NULL
);

-- ── Table 3: LDR — Ambient Light Sensor ──────────────────────────────────
-- Purpose: Monitor ambient light exposure — key factor for melatonin and sleep quality.
-- Sleep thresholds:
--   lux_percent < 5%   → ideal darkness for sleep
--   5% – 30%           → dim light — acceptable
--   > 30%              → bright light — disrupts melatonin / poor sleep condition
CREATE TABLE ldr_readings (
    id           BIGSERIAL PRIMARY KEY,
    lux_percent  DOUBLE PRECISION NOT NULL,   -- 0–100% (0=dark, 100=max bright)
    voltage      DOUBLE PRECISION NOT NULL,   -- ADC voltage 0–3.3V
    light_status VARCHAR(20)     NOT NULL,    -- 'IDEAL' | 'DIM' | 'BRIGHT'
    recorded_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    device_id    VARCHAR(60)     NOT NULL
);

-- ── Table 4: Sleep Sessions — aggregated per session ─────────────────────
-- Purpose: Store aggregated sleep quality score computed per session.
CREATE TABLE sleep_sessions (
    id                BIGSERIAL PRIMARY KEY,
    device_id         VARCHAR(60)     NOT NULL,
    session_start     TIMESTAMPTZ     NOT NULL,
    session_end       TIMESTAMPTZ,
    avg_heart_rate    DOUBLE PRECISION,
    avg_spo2          DOUBLE PRECISION,
    avg_movement      DOUBLE PRECISION,
    avg_light         DOUBLE PRECISION,
    sleep_score       INTEGER,                 -- 0–100 composite score
    sleep_quality     VARCHAR(20),             -- 'GOOD' | 'REGULAR' | 'POOR'
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ── Indexes for fast dashboard queries ───────────────────────────────────
CREATE INDEX idx_mpu_device_time  ON mpu6050_readings  (device_id, recorded_at DESC);
CREATE INDEX idx_max_device_time  ON max30102_readings  (device_id, recorded_at DESC);
CREATE INDEX idx_ldr_device_time  ON ldr_readings       (device_id, recorded_at DESC);
CREATE INDEX idx_session_device   ON sleep_sessions     (device_id, session_start DESC);

-- ── Enable Row Level Security (Supabase best practice) ───────────────────
ALTER TABLE mpu6050_readings  ENABLE ROW LEVEL SECURITY;
ALTER TABLE max30102_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ldr_readings      ENABLE ROW LEVEL SECURITY;
ALTER TABLE sleep_sessions    ENABLE ROW LEVEL SECURITY;

-- Allow all for service role (backend uses service role key)
CREATE POLICY "allow_all_service" ON mpu6050_readings  FOR ALL USING (true);
CREATE POLICY "allow_all_service" ON max30102_readings FOR ALL USING (true);
CREATE POLICY "allow_all_service" ON ldr_readings      FOR ALL USING (true);
CREATE POLICY "allow_all_service" ON sleep_sessions    FOR ALL USING (true);
