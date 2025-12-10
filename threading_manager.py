import threading
import cv2
import time
import queue
import config

class VideoThread(threading.Thread):
    def __init__(self, detector, frame_queue):
        super().__init__()
        self.detector = detector
        self.frame_queue = frame_queue
        self.running = True
        self.detection_active = False
        self.benchmark_active = False
        self.benchmark_start_time = 0
        self.benchmark_duration = 0
        self.benchmark_data = [] # List of (fps, latency)

        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    def run(self):
        prev_frame_time = 0
        new_frame_time = 0

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            faces = []
            latency = 0
            
            # Detection Logic
            if self.detection_active or self.benchmark_active:
                # Detector returns ({'faces':..., 'objects':...}, latency)
                results_dict, latency = self.detector.detect(frame)
                
                # Check for legacy faces list just in case detector isn't updated? 
                # No, we updated it. 
                # extract faces for queue/fps logic if needed? 
                # Actually, queue just passes it through.
                # Update variable 'faces' to be valid for queue tuple if needed
                # But we can just pass results_dict in place of 'faces' in queue tuple
                # The queue was: (frame, faces, fps, latency, benchmark_active)
                # We will change it to: (frame, results_dict, fps, latency, benchmark_active)
                faces = results_dict

                # Benchmark Storage
                if self.benchmark_active:
                    self.benchmark_data.append(latency)
                    if time.time() - self.benchmark_start_time > self.benchmark_duration:
                        self.benchmark_active = False
                        # Notify GUI or Main that benchmark is done (via queue or callback? 
                        # simpler to just let GUI poll or use a specific event, 
                        # but here we'll just stop collecting). 
                        print("Benchmark complete.")

            # FPS Calculation
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time > 0 else 0
            prev_frame_time = new_frame_time
            
            # Push to Queue (drop if full to avoid lag)
            if not self.frame_queue.full():
                self.frame_queue.put((frame, faces, fps, latency, self.benchmark_active))

            # Maintain Target FPS (optional sleep)
            # time.sleep(max(0, 1/config.TARGET_FPS - (time.time() - new_frame_time)))

        self.cap.release()

    def start_detection(self):
        self.detection_active = True

    def stop_detection(self):
        self.detection_active = False

    def start_benchmark(self, duration=10):
        self.benchmark_data = []
        self.benchmark_duration = duration
        self.benchmark_start_time = time.time()
        self.benchmark_active = True

    def get_benchmark_results(self):
        if not self.benchmark_data:
            return 0, 0
        avg_latency = sum(self.benchmark_data) / len(self.benchmark_data)
        avg_fps = 1000 / avg_latency if avg_latency > 0 else 0
        return avg_fps, avg_latency

    def stop(self):
        self.running = False
        self.join()
