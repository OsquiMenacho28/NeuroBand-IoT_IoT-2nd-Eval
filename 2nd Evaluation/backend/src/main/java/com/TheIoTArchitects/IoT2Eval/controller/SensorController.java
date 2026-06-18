package com.TheIoTArchitects.IoT2Eval.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import com.TheIoTArchitects.IoT2Eval.model.Dtos.DataPoint;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.LdrRequest;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.Max30102Request;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.Mpu6050Request;
import com.TheIoTArchitects.IoT2Eval.model.Dtos.StatusResponse;
import com.TheIoTArchitects.IoT2Eval.service.SensorService;
import com.TheIoTArchitects.IoT2Eval.service.SseService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class SensorController {

    private final SensorService sensorService;
    private final SseService sseService;

    // ── SSE — Vue dashboard subscribes here ──────────────────
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream() {
        return sseService.subscribe();
    }

    // ── Health check ─────────────────────────────────────────
    @GetMapping("/status")
    public ResponseEntity<StatusResponse> status() {
        StatusResponse r = new StatusResponse();
        r.setOnline(true);
        r.setConnectedFrontends(sseService.getConnectedCount());
        return ResponseEntity.ok(r);
    }

    // ── MPU6050 — Motion Sensor ───────────────────────────────
    @PostMapping("/mpu6050")
    public ResponseEntity<DataPoint> postMpu6050(
            @Valid @RequestBody Mpu6050Request req) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(sensorService.saveMpu6050(req));
    }

    @GetMapping("/mpu6050")
    public ResponseEntity<List<DataPoint>> getMpu6050() {
        return ResponseEntity.ok(sensorService.getAllMpu6050());
    }

    // ── MAX30102 — Heart Rate & SpO2 ──────────────────────────
    @PostMapping("/max30102")
    public ResponseEntity<DataPoint> postMax30102(
            @Valid @RequestBody Max30102Request req) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(sensorService.saveMax30102(req));
    }

    @GetMapping("/max30102")
    public ResponseEntity<List<DataPoint>> getMax30102() {
        return ResponseEntity.ok(sensorService.getAllMax30102());
    }

    // ── LDR — Ambient Light ───────────────────────────────────
    @PostMapping("/ldr")
    public ResponseEntity<DataPoint> postLdr(
            @Valid @RequestBody LdrRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(sensorService.saveLdr(req));
    }

    @GetMapping("/ldr")
    public ResponseEntity<List<DataPoint>> getLdr() {
        return ResponseEntity.ok(sensorService.getAllLdr());
    }
}