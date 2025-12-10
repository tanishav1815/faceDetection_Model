# 👁️ Sentinel: AI Vision System

> **"Seeing beyond the frame."**

![AI Vision](https://img.shields.io/badge/AI-Powered-blueviolet) ![Status](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)

**Sentinel** is a high-performance, real-time computer vision application designed to turn your webcam into an intelligent observer. It doesn't just see pixels; it understands **people**, **genders**, and **objects**.

Built with a robust multithreaded architecture, Sentinel combines classic Computer Vision (Haar Cascades) with state-of-the-art Deep Learning (YOLOv4, Caffe) to deliver a seamless detection experience.

---

## 🚀 Features

### 🧠 **Triple-Threat Detection Engine**
*   **👤 Face Detection**: Instantly locks onto human faces with millisecond precision using accelerated Haar Cascades.
*   **⚧ Gender Recognition**: Analyzes facial features to predict gender (Male/Female) in real-time.
*   **📦 Object Recognition (YOLOv4)**: Leveraging the massive **YOLOv4 High-Accuracy Model**, Sentinel identifies **80+ types of objects** including:
    *   📱 **Tech**: Cell phones, laptops, remotes, keyboards.
    *   🏠 **Household**: Bottles, cups, books, scissors, vases.
    *   🚗 **Transport**: Cars, bicycles, buses.
    *   ...and much more!

### ⚡ **High-Performance Architecture**
*   **Multithreaded Core**: Video capture and AI inference run on separate threads, ensuring your UI remains buttery smooth while the brain crunches numbers.
*   **Smart GPU Offloading**: Automatically detects CUDA-enabled GPUs to accelerate processing (with graceful CPU fallback).

### 📊 **Data-Driven Insights**
*   **MySQL Integration**: Automatically logs every detection event and performance benchmark into a local database.
*   **Benchmarking Mode**: Press a button to stress-test your system and record Frame-Time and Latency metrics.

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/tanishav1815/faceDetection_Model.git
cd faceDetection_Model
```

### 2. Setup Environment
We recommend using a virtual environment.
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup (Optional)
Sentinel uses MySQL for logging. Ensure you have a MySQL server running (default user `root`, no password).
*   *Note*: The app works even without the database (it will just skip logging).
*   To check logs later: `USE face_detection_db; SELECT * FROM detections;`

---

## 🎮 Usage

Simply run the main script. The system handles the rest, including **automatically downloading** the massive AI models (245MB+) on the first run.

```bash
python main.py
```

### **Controls**
| Key | Action |
| :--- | :--- |
| **`S`** | **Start/Stop** the AI Detection engine. |
| **`B`** | Run a **10-Second Benchmark** test. |
| **`G`** | Toggle **GPU/CPU** mode (if hardware supported). |
| **`Q`** | **Quit** the application safely. |

---

## 🏗️ Under the Hood

### **The Stack**
*   **Language**: Python 3.9+
*   **Vision**: OpenCV 4.12 (DNN Module)
*   **Models**:
    *   *YOLOv4 (Darknet)*: For general object detection.
    *   *Caffe (GoogLeNet)*: For age/gender classification.
    *   *Haar Cascades*: For rapid face localization.
*   **Data**: MySQL Connector

### **Configuration**
Check `config.py` to tweak settings:
*   `USE_FULL_YOLO_MODEL`: Set to `True` for accuracy (default), `False` for speed (Tiny mode).
*   `CAMERA_INDEX`: Change if you have multiple webcams.
*   `DB_CONFIG`: Update your database credentials.

---

## 🤝 Contributing

Got an idea to make Sentinel smarter?
1.  Fork the repo.
2.  Create a branch: `git checkout -b feature/super-vision`
3.  Commit changes: `git commit -m 'Add x-ray vision'`
4.  Push: `git push origin feature/super-vision`
5.  Open a Pull Request!

---

> *Built with code and caffeine by Tanisha.*
