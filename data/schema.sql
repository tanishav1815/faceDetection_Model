CREATE DATABASE IF NOT EXISTS face_detection_db;
USE face_detection_db;

CREATE TABLE IF NOT EXISTS detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    faces_detected INT,
    mode VARCHAR(10), -- 'CPU' or 'GPU'
    fps FLOAT,
    latency_ms FLOAT
);

CREATE TABLE IF NOT EXISTS benchmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_fps FLOAT,
    gpu_fps FLOAT,
    cpu_latency_ms FLOAT,
    gpu_latency_ms FLOAT,
    notes TEXT
);
