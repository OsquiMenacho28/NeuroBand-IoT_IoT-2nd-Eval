package com.TheIoTArchitects.IoT2Eval.model;

import java.time.OffsetDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * MPU6050 — 6-axis Accelerometer & Gyroscope readings.
 * Used to detect body movement and sleep restlessness.
 *
 * Sleep movement thresholds:
 * accelMagnitude < 0.15 g → STILL (deep sleep)
 * 0.15 – 0.50 g → LIGHT (REM / light sleep)
 * > 0.50 g → ACTIVE (awake or restless)
 */
@Entity
@Table(name = "mpu6050_readings")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Mpu6050Reading {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "accel_x", nullable = false)
    private Double accelX;
    @Column(name = "accel_y", nullable = false)
    private Double accelY;
    @Column(name = "accel_z", nullable = false)
    private Double accelZ;
    @Column(name = "gyro_x", nullable = false)
    private Double gyroX;
    @Column(name = "gyro_y", nullable = false)
    private Double gyroY;
    @Column(name = "gyro_z", nullable = false)
    private Double gyroZ;
    @Column(name = "accel_magnitude", nullable = false)
    private Double accelMagnitude;

    /** STILL | LIGHT | ACTIVE */
    @Column(name = "movement_level", nullable = false, length = 20)
    private String movementLevel;

    @Column(name = "recorded_at", nullable = false)
    private OffsetDateTime recordedAt;

    @Column(name = "device_id", nullable = false, length = 60)
    private String deviceId;

    @PrePersist
    public void prePersist() {
        if (this.recordedAt == null)
            this.recordedAt = OffsetDateTime.now();
    }
}