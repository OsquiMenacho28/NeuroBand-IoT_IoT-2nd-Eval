package com.TheIoTArchitects.IoT2Eval.service;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import com.TheIoTArchitects.IoT2Eval.model.Dtos.DataPoint;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

/**
 * Maintains a list of SSE-connected frontends and broadcasts
 * a DataPoint event every time the ESP32 POSTs new sensor data.
 */
@Service
public class SseService {

    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final ObjectMapper mapper;

    public SseService() {
        this.mapper = new ObjectMapper();
        this.mapper.registerModule(new JavaTimeModule());
    }

    /** Vue dashboard subscribes here: GET /api/stream */
    public SseEmitter subscribe() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        emitters.add(emitter);

        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError(e -> emitters.remove(emitter));

        // Send a welcome ping to confirm connection
        try {
            emitter.send(SseEmitter.event()
                    .name("ping")
                    .data("{\"status\":\"connected\",\"project\":\"NeuroBand IoT\"}"));
        } catch (IOException e) {
            emitters.remove(emitter);
        }
        return emitter;
    }

    /** Called after every successful sensor INSERT */
    public void broadcast(DataPoint point) {
        List<SseEmitter> dead = new CopyOnWriteArrayList<>();
        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event()
                        .name("sensor-data")
                        .data(mapper.writeValueAsString(point)));
            } catch (IOException e) {
                dead.add(emitter);
            }
        }
        emitters.removeAll(dead);
    }

    public int getConnectedCount() {
        return emitters.size();
    }
}