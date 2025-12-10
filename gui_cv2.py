import cv2
import time
import queue
from db import DatabaseManager

class CV2GUI:
    def __init__(self, root, db_manager, video_thread, detector):
        self.db = db_manager
        self.thread = video_thread
        self.detector = detector
        
        self.is_detecting = False
        self.is_benchmarking = False
        
        # Start Video Thread
        self.thread.start()
        
        self.window_name = "Face Detection App (CV2 Fallback)"
        cv2.namedWindow(self.window_name)
        
        # Instructions
        print("========================================")
        print("      CV2 FALLBACK GUI CONTROLS")
        print("========================================")
        print(" [S] - Start/Stop Detection")
        print(" [B] - Run Benchmark (10s)")
        print(" [G] - Toggle GPU/CPU Mode")
        print(" [Q] - Quit")
        print("========================================")

    def on_closing(self):
        self.thread.stop()
        self.db.close()
        cv2.destroyAllWindows()

    def run(self):
        while True:
            try:
                if not self.thread.frame_queue.empty():
                    frame_data = self.thread.frame_queue.get_nowait()
                    frame, detection_results, fps, latency, benchmark_active = frame_data
                    
                    # Unpack results
                    # detection_results is now a dict: {'faces': [(rect, gender)], 'objects': [(lbl, conf, rect)]}
                    # Or [] if no detection
                    
                    curr_faces = []
                    curr_objects = []
                    
                    if isinstance(detection_results, dict):
                        curr_faces = detection_results.get('faces', [])
                        curr_objects = detection_results.get('objects', [])
                    elif isinstance(detection_results, list):
                        # Legacy support if simple tuple returned? No, we updated detection.py
                        # But handle empty case
                        curr_faces = [] 
                    
                    # Draw Objects
                    for (label, conf, (x, y, w, h)) in curr_objects:
                        # Don't draw 'person' if it overlaps significantly with face? 
                        # Actually 'person' detects the whole body. Face detects face.
                        # Maybe draw all.
                        color = (255, 0, 0) # Blue for objects
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        text = f"{label} {conf*100:.0f}%"
                        cv2.putText(frame, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    # Draw Faces & Gender
                    for ((x, y, w, h), gender) in curr_faces:
                        color = (0, 255, 0) # Green for faces
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        
                        # Label: "Male" or "Female"
                        label_color = (255, 100, 100) if gender == "Female" else (100, 100, 255)
                        cv2.putText(frame, gender, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)
                    
                    # Stats Loop
                    mode_str = "GPU" if self.detector.use_cuda else "CPU"
                    stats_text = [
                        f"FPS: {fps:.1f}",
                        f"Latency: {latency:.1f} ms",
                        f"Faces: {len(curr_faces)}",
                        f"Objects: {len(curr_objects)}",
                        f"Mode: {mode_str}",
                        " Controls: [S]tart/Stop [B]enchmark [G]PU [Q]uit"
                    ]
                    
                    y0, dy = 30, 25
                    for i, line in enumerate(stats_text):
                        y = y0 + i*dy
                        cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    if benchmark_active:
                         cv2.putText(frame, "BENCHMARKING...", (10, y0 + len(stats_text)*dy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                    cv2.imshow(self.window_name, frame)
                    
                # Handle Keys
                key = cv2.waitKey(10) & 0xFF
                
                if key == ord('q'):
                    self.on_closing()
                    break
                elif key == ord('s'):
                    if self.thread.detection_active:
                        self.thread.stop_detection()
                    else:
                        self.thread.start_detection()
                elif key == ord('b'):
                    self.thread.start_benchmark(duration=10)
                elif key == ord('g'):
                    new_mode = not self.detector.use_cuda
                    self.detector.set_mode(new_mode)

                if self.is_benchmarking and not self.thread.benchmark_active:
                    self.is_benchmarking = False
                    fps_res, lat_res = self.thread.get_benchmark_results()
                    
                    # Log to DB (assume CPU only for now logic simplicity, or get mode from detector)
                    mode_is_gpu = self.detector.use_cuda
                    self.db.log_benchmark(
                        fps_res if not mode_is_gpu else 0,
                        fps_res if mode_is_gpu else 0,
                        lat_res if not mode_is_gpu else 0,
                        lat_res if mode_is_gpu else 0
                    )
                    print(f"Benchmark Logged: FPS={fps_res:.2f}, Latency={lat_res:.2f}")

                if self.thread.benchmark_active:
                    self.is_benchmarking = True

            except queue.Empty:
                pass
            except KeyboardInterrupt:
                self.on_closing()
                break
