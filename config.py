import os

# Database Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "NewPassword123!" # User should update this
DB_NAME = "face_detection_db"

# Camera Configuration
CAMERA_INDEX = 0  # Default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Detection Configuration
HAAR_CASCADE_FILENAME = "haarcascade_frontalface_default.xml"
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_SIZE = (30, 30)

# Performance
TARGET_FPS = 30

# GUI Backend ('tk' or 'cv2')
# Use 'cv2' if Tkinter crashes on macOS
GUI_BACKEND = 'cv2'

# Feature Toggles
ENABLE_GENDER_DETECTION = True
ENABLE_OBJECT_DETECTION = True

# Models
GENDER_MODEL_URLS = {
    # Backup Source: https://github.com/smahesh29/Gender-and-Age-Detection
    "gender_proto": "https://raw.githubusercontent.com/smahesh29/Gender-and-Age-Detection/master/gender_deploy.prototxt",
    "gender_model": "https://github.com/smahesh29/Gender-and-Age-Detection/raw/master/gender_net.caffemodel"
}
# Using local filenames
GENDER_PROTO = "gender_deploy.prototxt"
GENDER_MODEL = "gender_net.caffemodel"
GENDER_MEAN = (78.4263377603, 87.7689143744, 114.895847746)
GENDER_LIST = ['Male', 'Female']

# YOLOv4-tiny
OBJECT_CONFIG_TINY = "yolov4-tiny.cfg"
OBJECT_WEIGHTS_TINY = "yolov4-tiny.weights"

# YOLOv4 Full (High Accuracy)
OBJECT_CONFIG_FULL = "yolov4.cfg"
OBJECT_WEIGHTS_FULL = "yolov4.weights"

OBJECT_NAMES = "coco.names"

# Toggle: Set to True for High Accuracy (Slower), False for Fast (Tiny)
USE_FULL_YOLO_MODEL = True

# Sources
OBJECT_MODEL_URL_NAMES = "https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names"

# Tiny URLs
OBJECT_MODEL_URL_CONFIG_TINY = "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg"
OBJECT_MODEL_URL_WEIGHTS_TINY = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights"

# Full URLs
OBJECT_MODEL_URL_CONFIG_FULL = "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg"
OBJECT_MODEL_URL_WEIGHTS_FULL = "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights"

OBJECT_CLASSES = [] # Will be loaded from coco.names

