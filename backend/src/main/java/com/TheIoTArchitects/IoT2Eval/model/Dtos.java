package com.TheIoTArchitects.IoT2Eval.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

public class Dtos {

    // ─────────────────────────────────────────────────────────
    // Inbound — payloads sent by the ESP32 via HTTP POST
    // ─────────────────────────────────────────────────────────

    /** MPU6050 payload from ESP32 */
    @Data
    public static class Mpu6050Request {
        @NotBlank
        private String deviceId;
        @NotNull
        private Double accelX;
        @NotNull
        private Double accelY;
        @NotNull
        private Double accelZ;
        @NotNull
        private Double gyroX;
        @NotNull
        private Double gyroY;
        @NotNull
        private Double gyroZ;
    }

    /** MAX30102 payload from ESP32 */
    @Data
    public static class Max30102Request {
        @NotBlank
        private String deviceId;
        @NotNull
        private Double heartRate;
        @NotNull
        private Double spo2;
        @NotNull
        private Long irValue;
        @NotNull
        private Long redValue;
    }

    /** LDR payload from ESP32 */
    @Data
    public static class LdrRequest {
        @NotBlank
        private String deviceId;
        @NotNull
        private Double luxPercent;
        @NotNull
        private Double voltage;
    }

    // ─────────────────────────────────────────────────────────
    // Outbound — unified DataPoint for SSE stream & REST responses
    // ─────────────────────────────────────────────────────────

    @Data
    public static class DataPoint {
        private Long id;
        private String sensor; // "mpu6050" | "max30102" | "ldr"
        private String deviceId;
        private String recordedAt;

        // MPU6050 fields
        private Double accelX;
        private Double accelY;
        private Double accelZ;
        private Double gyroX;
        private Double gyroY;
        private Double gyroZ;
        private Double accelMagnitude;
        private String movementLevel; // STILL | LIGHT | ACTIVE

        // MAX30102 fields
        private Double heartRate;
        private Double spo2;
        private Long irValue;
        private Long redValue;
        private String hrStatus; // DEEP_SLEEP | RESTING | AWAKE
        private String spo2Status; // HEALTHY | MILD_HYPOXIA | CRITICAL

        // LDR fields
        private Double luxPercent;
        private Double voltage;
        private String lightStatus; // IDEAL | DIM | BRIGHT
    }

    // ─────────────────────────────────────────────────────────
    // API health response
    // ─────────────────────────────────────────────────────────

    @Data
    public static class StatusResponse {
        private boolean online;
        private int connectedFrontends;
        private String version = "1.0.0";
        private String project = "NeuroBand IoT";
    }
}