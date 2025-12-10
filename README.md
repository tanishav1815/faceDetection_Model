# Face Detection Desktop App

A production-ready real-time face detection application built with Python, OpenCV, Tkinter, and MySQL.

## Features
- **Real-time Face Detection**: Uses Haar Cascades.
- **Performance Optimized**: Multithreaded video processing to maintain UI responsiveness.
- **Hardware Acceleration**: Supports GPU acceleration via CUDA (if available) with CPU fallback.
- **Data Logging**: Logs detection events and benchmark metrics to a MySQL database.
- **GUI Controls**: Start/Stop detection, GPU toggle, and Benchmark mode.

## Requirements
- Python 3.x
- MySQL Server (running on localhost)

## Installation

1.  **Clone the repository/folder**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `opencv-python` is used. For GPU support, ensure you have CUDA installed and a compatible OpenCV build, or install `opencv-python` and rely on CPU fallback).*
3.  **Database Setup**:
    - Ensure your MySQL server is running.
    - Update `config.py` with your MySQL credentials (password primarily).
    ```python
    # config.py
    DB_PASSWORD = "your_password"
    ```

## Usage

1.  **Run the Application**:
    ```bash
    python main.py
    ```
    - The app will automatically initialize the database `face_detection_db` and tables.
    - It will check for the Haar Cascade XML and copy it to `data/` if needed.

2.  **Controls**:
    - **Start Detection**: specific button to enable face detection overlays.
    - **Mode**: Toggle between CPU and GPU (requires CUDA) for detection.
    - **Run Benchmark**: Runs a 10-second performance test and logs FPS/Latency to the database.

## Folder Structure
- `main.py`: Entry point.
- `gui.py`: Tkinter GUI implementation.
- `detection.py`: Face detection logic (Haar/CUDA).
- `threading_manager.py`: Video capture handling in separate thread.
- `db.py`: Database management.
- `config.py`: Application configuration.
- `data/`: Stores XML models and schema.
