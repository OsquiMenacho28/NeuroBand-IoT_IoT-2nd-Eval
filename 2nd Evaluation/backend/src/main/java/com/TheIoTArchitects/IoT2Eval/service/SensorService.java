package com.TheIoTArchitects.IoT2Eval.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.TheIoTArchitects.IoT2Eval.model.Dtos.DataPoint;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.LdrRequest;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.Max30102Request;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.Mpu6050Request;
import com.TheIoTArchitects.IoT2Eval.model.LdrReading;
import com.TheIoTArchitects.IoT2Eval.model.Max30102Reading;
import com.TheIoTArchitects.IoT2Eval.model.Mpu6050Reading;
import com.TheIoTArchitects.IoT2Eval.repository.LdrRepository;
import com.TheIoTArchitects.IoT2Eval.repository.Max30102Repository;
import com.TheIoTArchitects.IoT2Eval.repository.Mpu6050Repository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class SensorService {

    private final Mpu6050Repository mpuRepo;
    private final Max30102Repository maxRepo;
    private final LdrRepository ldrRepo;
    private final SseService sse;
    private final ThresholdEvaluator threshold;

    // ── MPU6050 ───────────────────────────────────────────────────────────

    @Transactional
    public DataPoint saveMpu6050(Mpu6050Request req) {
        double magnitude = threshold.computeMagnitude(req.getAccelX(), req.getAccelY(), req.getAccelZ());
        String level = threshold.evaluateMovement(magnitude);

        Mpu6050Reading saved = mpuRepo.save(Mpu6050Reading.builder()
                .deviceId(req.getDeviceId())
                .accelX(req.getAccelX())
                .accelY(req.getAccelY())
                .accelZ(req.getAccelZ())
                .gyroX(req.getGyroX())
                .gyroY(req.getGyroY())
                .gyroZ(req.getGyroZ())
                .accelMagnitude(magnitude)
                .movementLevel(level)
                .build());

        DataPoint dp = toDataPoint(saved);
        sse.broadcast(dp);
        return dp;
    }

    public List<DataPoint> getAllMpu6050() {
        return mpuRepo.findAllByOrderByRecordedAtAsc()
                .stream().map(this::toDataPoint).collect(Collectors.toList());
    }

    // ── MAX30102 ──────────────────────────────────────────────────────────

    @Transactional
    public DataPoint saveMax30102(Max30102Request req) {
        String hrStatus = threshold.evaluateHeartRate(req.getHeartRate());
        String spo2Status = threshold.evaluateSpo2(req.getSpo2());

        Max30102Reading saved = maxRepo.save(Max30102Reading.builder()
                .deviceId(req.getDeviceId())
                .heartRate(req.getHeartRate())
                .spo2(req.getSpo2())
                .irValue(req.getIrValue())
                .redValue(req.getRedValue())
                .hrStatus(hrStatus)
                .spo2Status(spo2Status)
                .build());

        DataPoint dp = toDataPoint(saved);
        sse.broadcast(dp);
        return dp;
    }

    public List<DataPoint> getAllMax30102() {
        return maxRepo.findAllByOrderByRecordedAtAsc()
                .stream().map(this::toDataPoint).collect(Collectors.toList());
    }

    // ── LDR ───────────────────────────────────────────────────────────────

    @Transactional
    public DataPoint saveLdr(LdrRequest req) {
        String lightStatus = threshold.evaluateLight(req.getLuxPercent());

        LdrReading saved = ldrRepo.save(LdrReading.builder()
                .deviceId(req.getDeviceId())
                .luxPercent(req.getLuxPercent())
                .voltage(req.getVoltage())
                .lightStatus(lightStatus)
                .build());

        DataPoint dp = toDataPoint(saved);
        sse.broadcast(dp);
        return dp;
    }

    public List<DataPoint> getAllLdr() {
        return ldrRepo.findAllByOrderByRecordedAtAsc()
                .stream().map(this::toDataPoint).collect(Collectors.toList());
    }

    // ── Mappers ───────────────────────────────────────────────────────────

    private DataPoint toDataPoint(Mpu6050Reading r) {
        DataPoint dp = new DataPoint();
        dp.setSensor("mpu6050");
        dp.setId(r.getId());
        dp.setDeviceId(r.getDeviceId());
        dp.setRecordedAt(r.getRecordedAt().toString());
        dp.setAccelX(r.getAccelX());
        dp.setAccelY(r.getAccelY());
        dp.setAccelZ(r.getAccelZ());
        dp.setGyroX(r.getGyroX());
        dp.setGyroY(r.getGyroY());
        dp.setGyroZ(r.getGyroZ());
        dp.setAccelMagnitude(r.getAccelMagnitude());
        dp.setMovementLevel(r.getMovementLevel());
        return dp;
    }

    private DataPoint toDataPoint(Max30102Reading r) {
        DataPoint dp = new DataPoint();
        dp.setSensor("max30102");
        dp.setId(r.getId());
        dp.setDeviceId(r.getDeviceId());
        dp.setRecordedAt(r.getRecordedAt().toString());
        dp.setHeartRate(r.getHeartRate());
        dp.setSpo2(r.getSpo2());
        dp.setIrValue(r.getIrValue());
        dp.setRedValue(r.getRedValue());
        dp.setHrStatus(r.getHrStatus());
        dp.setSpo2Status(r.getSpo2Status());
        return dp;
    }

    private DataPoint toDataPoint(LdrReading r) {
        DataPoint dp = new DataPoint();
        dp.setSensor("ldr");
        dp.setId(r.getId());
        dp.setDeviceId(r.getDeviceId());
        dp.setRecordedAt(r.getRecordedAt().toString());
        dp.setLuxPercent(r.getLuxPercent());
        dp.setVoltage(r.getVoltage());
        dp.setLightStatus(r.getLightStatus());
        return dp;
    }
}