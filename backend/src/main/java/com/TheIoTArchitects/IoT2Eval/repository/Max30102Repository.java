package com.TheIoTArchitects.IoT2Eval.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.TheIoTArchitects.IoT2Eval.model.Max30102Reading;

public interface Max30102Repository extends JpaRepository<Max30102Reading, Long> {
    List<Max30102Reading> findAllByOrderByRecordedAtAsc();

    List<Max30102Reading> findByDeviceIdOrderByRecordedAtAsc(String deviceId);

    @Query("SELECT r FROM Max30102Reading r ORDER BY r.recordedAt DESC LIMIT :n")
    List<Max30102Reading> findLatest(@Param("n") int n);
}