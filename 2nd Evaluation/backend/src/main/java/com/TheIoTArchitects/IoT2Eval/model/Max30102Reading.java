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
 * MAX30102 — Optical heart rate & SpO2 (blood oxygen) sensor readings.
 *
 * Sleep thresholds:
 * heartRate: 40–60 bpm → DEEP_SLEEP (bradycardia, normal during deep sleep)
 * 60–80 bpm → RESTING (light sleep or relaxed awake)
 * > 80 bpm → AWAKE (active / stressed)
 *
 * spo2: ≥ 95% → HEALTHY
 * 90–94% → MILD_HYPOXIA (alert the user)
 * < 90% → CRITICAL (urgent alert)
 */
@Entity
@Table(name = "max30102_readings")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Max30102Reading {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "heart_rate", nullable = false)
    private Double heartRate;
    @Column(name = "spo2", nullable = false)
    private Double spo2;
    @Column(name = "ir_value", nullable = false)
    private Long irValue;
    @Column(name = "red_value", nullable = false)
    private Long redValue;

    /** DEEP_SLEEP | RESTING | AWAKE */
    @Column(name = "hr_status", nullable = false, length = 20)
    private String hrStatus;

    /** HEALTHY | MILD_HYPOXIA | CRITICAL */
    @Column(name = "spo2_status", nullable = false, length = 20)
    private String spo2Status;

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