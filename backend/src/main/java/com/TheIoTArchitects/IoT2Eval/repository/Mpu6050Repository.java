package com.TheIoTArchitects.IoT2Eval.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.TheIoTArchitects.IoT2Eval.model.Mpu6050Reading;

public interface Mpu6050Repository extends JpaRepository<Mpu6050Reading, Long> {

    List<Mpu6050Reading> findAllByOrderByRecordedAtAsc();

    List<Mpu6050Reading> findByDeviceIdOrderByRecordedAtAsc(String deviceId);

    /** Latest N readings for live chart streaming */
    @Query("SELECT r FROM Mpu6050Reading r ORDER BY r.recordedAt DESC LIMIT :n")
    List<Mpu6050Reading> findLatest(@Param("n") int n);
}