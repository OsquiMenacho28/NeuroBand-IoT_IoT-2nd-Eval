package com.TheIoTArchitects.IoT2Eval.service;

import org.springframework.stereotype.Component;

/**
 * Evaluates sensor readings against NeuroBand IoT sleep quality thresholds.
 *
 * These thresholds are based on sleep medicine research:
 * - Movement: American Academy of Sleep Medicine (AASM) actigraphy guidelines
 * - Heart rate: Normal bradycardia ranges during sleep stages
 * - SpO2: WHO / clinical hypoxia classification
 * - Light: Melatonin suppression research (lux thresholds for sleep onset)
 */
@Component
public class ThresholdEvaluator {

    // ── MPU6050 Movement Thresholds ───────────────────────────────────────
    public static final double MOVEMENT_STILL_MAX = 0.15; // g — deep sleep
    public static final double MOVEMENT_LIGHT_MAX = 0.50; // g — REM / light sleep
    // > 0.50 g → ACTIVE (restless or awake)

    // ── MAX30102 Heart Rate Thresholds (bpm) ─────────────────────────────
    public static final double HR_DEEP_SLEEP_MIN = 40.0;
    public static final double HR_DEEP_SLEEP_MAX = 60.0;
    public static final double HR_RESTING_MAX = 80.0;
    // > 80 → AWAKE

    // ── MAX30102 SpO2 Thresholds (%) ─────────────────────────────────────
    public static final double SPO2_HEALTHY_MIN = 95.0; // ≥ 95 → HEALTHY
    public static final double SPO2_MILD_HYPOXIA_MIN = 90.0; // 90–94 → MILD_HYPOXIA
    // < 90 → CRITICAL

    // ── LDR Light Thresholds (%) ─────────────────────────────────────────
    public static final double LIGHT_IDEAL_MAX = 5.0; // < 5% → IDEAL (dark)
    public static final double LIGHT_DIM_MAX = 30.0; // 5–30% → DIM
    // > 30% → BRIGHT (disrupts melatonin)

    // ─────────────────────────────────────────────────────────────────────

    public String evaluateMovement(double magnitude) {
        if (magnitude < MOVEMENT_STILL_MAX)
            return "STILL";
        if (magnitude < MOVEMENT_LIGHT_MAX)
            return "LIGHT";
        return "ACTIVE";
    }

    public String evaluateHeartRate(double bpm) {
        if (bpm >= HR_DEEP_SLEEP_MIN && bpm <= HR_DEEP_SLEEP_MAX)
            return "DEEP_SLEEP";
        if (bpm <= HR_RESTING_MAX)
            return "RESTING";
        return "AWAKE";
    }

    public String evaluateSpo2(double spo2) {
        if (spo2 >= SPO2_HEALTHY_MIN)
            return "HEALTHY";
        if (spo2 >= SPO2_MILD_HYPOXIA_MIN)
            return "MILD_HYPOXIA";
        return "CRITICAL";
    }

    public String evaluateLight(double luxPercent) {
        if (luxPercent < LIGHT_IDEAL_MAX)
            return "IDEAL";
        if (luxPercent < LIGHT_DIM_MAX)
            return "DIM";
        return "BRIGHT";
    }

    /** Compute acceleration vector magnitude from XYZ components */
    public double computeMagnitude(double x, double y, double z) {
        return Math.sqrt(x * x + y * y + z * z);
    }
}