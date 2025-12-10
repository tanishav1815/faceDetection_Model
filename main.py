import cv2
import queue
import setup_data
from db import DatabaseManager
from detection import FaceDetector
from threading_manager import VideoThread
import config

def main():
    print("Starting Face Detection App...")
    
    # Ensure data exists
    setup_data.setup()
    
    # Initialize Database
    print("Initializing Database...")
    db = DatabaseManager()
    
    # Initialize Face Detector
    print("Initializing Detector...")
    detector = FaceDetector()
    
    # Communication Queue
    frame_queue = queue.Queue(maxsize=1)
    
    # Initialize Video Thread
    print("Starting Video Thread...")
    video_thread = VideoThread(detector, frame_queue)
    
    # Initialize GUI
    print(f"Starting GUI ({config.GUI_BACKEND})...")
    
    if config.GUI_BACKEND == 'tk':
        import tkinter as tk
        from gui import FaceDetectionApp
        root = tk.Tk()
        app = FaceDetectionApp(root, db, video_thread, detector)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    else:
        from gui_cv2 import CV2GUI
        app = CV2GUI(None, db, video_thread, detector)
        app.run()

if __name__ == "__main__":
    main()
