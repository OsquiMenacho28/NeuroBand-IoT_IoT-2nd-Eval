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
 * LDR — Ambient light sensor readings.
 * Monitors bedroom light conditions — critical for melatonin production.
 *
 * Sleep thresholds:
 * luxPercent < 5% → IDEAL (dark room, best for sleep)
 * 5% – 30% → DIM (acceptable dim light)
 * > 30% → BRIGHT (disrupts melatonin, poor sleep condition)
 */
@Entity
@Table(name = "ldr_readings")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LdrReading {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "lux_percent", nullable = false)
    private Double luxPercent;
    @Column(name = "voltage", nullable = false)
    private Double voltage;

    /** IDEAL | DIM | BRIGHT */
    @Column(name = "light_status", nullable = false, length = 20)
    private String lightStatus;

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