import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import queue
import time
import config

class FaceDetectionApp:
    def __init__(self, root, db_manager, video_thread, detector):
        self.root = root
        self.root.title("Face Detection App")
        self.root.geometry("800x700")
        
        self.db = db_manager
        self.thread = video_thread
        self.detector = detector
        
        self.is_detecting = False
        self.is_benchmarking = False
        
        self.setup_ui()
        
        # Start Video Thread
        self.thread.start()
        
        # Start UI Update Loop
        self.root.after(10, self.update_ui)

    def setup_ui(self):
        # Top Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Start/Stop Button
        self.btn_toggle = ttk.Button(control_frame, text="Start Detection", command=self.toggle_detection)
        self.btn_toggle.pack(side="left", padx=5)
        
        # GPU/CPU Toggle
        ttk.Label(control_frame, text="Mode:").pack(side="left", padx=5)
        self.mode_var = tk.StringVar(value="CPU")
        self.combo_mode = ttk.Combobox(control_frame, textvariable=self.mode_var, values=["CPU", "GPU"], state="readonly")
        self.combo_mode.pack(side="left", padx=5)
        self.combo_mode.bind("<<ComboboxSelected>>", self.change_mode)
        
        # Benchmark Button
        self.btn_benchmark = ttk.Button(control_frame, text="Run Benchmark", command=self.run_benchmark)
        self.btn_benchmark.pack(side="left", padx=5)
        
        # Stats Frame
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_fps = ttk.Label(stats_frame, text="FPS: 0")
        self.lbl_fps.pack(side="left", padx=10)
        
        self.lbl_latency = ttk.Label(stats_frame, text="Latency: 0 ms")
        self.lbl_latency.pack(side="left", padx=10)
        
        self.lbl_faces = ttk.Label(stats_frame, text="Faces Detected: 0")
        self.lbl_faces.pack(side="left", padx=10)
        
        # Video Display
        self.video_frame = tk.Label(self.root)
        self.video_frame.pack(padx=10, pady=10)

    def toggle_detection(self):
        if self.is_detecting:
            self.thread.stop_detection()
            self.btn_toggle.config(text="Start Detection")
            self.is_detecting = False
        else:
            self.thread.start_detection()
            self.btn_toggle.config(text="Stop Detection")
            self.is_detecting = True

    def change_mode(self, event):
        mode = self.mode_var.get()
        use_gpu = (mode == "GPU")
        actual_gpu = self.detector.set_mode(use_gpu)
        
        if use_gpu and not actual_gpu:
            messagebox.showwarning("GPU Unavailable", "CUDA GPU is not available. Falling back to CPU.")
            self.mode_var.set("CPU")

    def run_benchmark(self):
        if self.is_benchmarking:
            return
            
        self.is_benchmarking = True
        self.btn_benchmark.config(state="disabled")
        messagebox.showinfo("Benchmark", "Running 10s benchmark...")
        self.thread.start_benchmark(duration=10)
        self.check_benchmark_status()

    def check_benchmark_status(self):
        if self.thread.benchmark_active:
            self.root.after(500, self.check_benchmark_status)
        else:
            # Benchmark done
            self.is_benchmarking = False
            self.btn_benchmark.config(state="normal")
            fps, latency = self.thread.get_benchmark_results()
            mode = self.mode_var.get()
            
            # Log to DB
            cpu_fps = fps if mode == "CPU" else 0
            gpu_fps = fps if mode == "GPU" else 0
            cpu_lat = latency if mode == "CPU" else 0
            gpu_lat = latency if mode == "GPU" else 0
            
            self.db.log_benchmark(cpu_fps, gpu_fps, cpu_lat, gpu_lat)
            messagebox.showinfo("Benchmark Complete", f"Avg FPS: {fps:.2f}\nAvg Latency: {latency:.2f} ms\n logged to DB.")

    def update_ui(self):
        try:
            # Empty the queue to get the latest frame
            # Wait, if we empty it we lose frames. Just get one.
            # But if processing is slow, queue builds up.
            # We should probably drain queue until empty or just get one.
            # Standard: Get one. If Main thread is slow, queue fills => thread drops frames.
            if not self.thread.frame_queue.empty():
                frame_data = self.thread.frame_queue.get_nowait()
                frame, faces, fps, latency, benchmark_active = frame_data
                
                # Draw faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Update Labels
                self.lbl_fps.config(text=f"FPS: {fps:.1f}")
                self.lbl_latency.config(text=f"Latency: {latency:.1f} ms")
                self.lbl_faces.config(text=f"Faces Detected: {len(faces)}")
                
                # Convert to ImageTk
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_frame.imgtk = imgtk
                self.video_frame.configure(image=imgtk)
                
                # Log detection to DB periodically or every frame?
                # User req: "Log: Each detection event."
                # Logging every frame with detection might be heavy.
                # Let's log if faces > 0.
                if len(faces) > 0:
                    mode = self.mode_var.get()
                    # To prevent DB flooding (30 inserts/sec), maybe logic here?
                    # The prompt implies "Each detection event".
                    # Realistically, we should maybe batch or only log on change.
                    # I'll log it as requested, but user beware of DB size.
                    # Or maybe I'll log once per second? 
                    # For a "production-ready" app, thousands of inserts/min is bad for a local app UI thread.
                    # But I'll stick to the requirement literally for now, or just delegate to a background task?
                    # `db.log_detection` is blocking. Doing it in UI thread will kill FPS.
                    # I should probably spawn a thread for logging or trust the DB is fast enough (it isn't).
                    # I'll fire-and-forget in a simple way or just accept the performance hit for this MVP.
                    # Better: The video thread could invoke DB logging asynchronously.
                    # Since I am in `update_ui` (Main Thread), blocking here freezes UI.
                    # I will assume for this task that direct logging is acceptable, or use a separate thread for logging.
                    # Optimally: Create a DBQueue and a DBWorker thread.
                    # I'll stick to direct call for simplicity unless it lags, but note it.
                    # Actually, I'll add a quick threaded call for logging to be safe.
                    threading.Thread(target=self.db.log_detection, args=(len(faces), mode, fps, latency)).start()

        except queue.Empty:
            pass
        
        self.root.after(10, self.update_ui)

    def on_closing(self):
        self.thread.stop()
        self.db.close()
        self.root.destroy()
