import cv2
import time
import os
import numpy as np
import config

class GenderDetector:
    def __init__(self):
        self.net = None
        self.enabled = config.ENABLE_GENDER_DETECTION
        if self.enabled:
             proto_path = os.path.join("data", config.GENDER_PROTO)
             model_path = os.path.join("data", config.GENDER_MODEL)
             if os.path.exists(proto_path) and os.path.exists(model_path):
                 print(f"Loading Gender Model from {model_path}")
                 self.net = cv2.dnn.readNet(model_path, proto_path)
             else:
                 print("Gender model files not found. Disabling gender detection.")
                 self.enabled = False

    def predict_gender(self, face_img):
        if not self.enabled or self.net is None:
            return "Unknown"
        
        try:
            blob = cv2.dnn.blobFromImage(face_img, 1.0, (227, 227), config.GENDER_MEAN, swapRB=False)
            self.net.setInput(blob)
            preds = self.net.forward()
            i = preds[0].argmax()
            gender = config.GENDER_LIST[i]
            confidence = preds[0][i]
            return gender
        except Exception as e:
            print(f"Gender Error: {e}")
            return "Error"

class ObjectDetector:
    def __init__(self):
        self.net = None
        self.classes = []
        self.layer_names = []
        self.output_layers = []
        self.enabled = config.ENABLE_OBJECT_DETECTION
        
        if self.enabled:
            if config.USE_FULL_YOLO_MODEL:
                print("Using Full YOLOv4 Model (High Accuracy)")
                config_path = os.path.join("data", config.OBJECT_CONFIG_FULL)
                weights_path = os.path.join("data", config.OBJECT_WEIGHTS_FULL)
            else:
                print("Using YOLOv4-tiny Model (High Speed)")
                config_path = os.path.join("data", config.OBJECT_CONFIG_TINY)
                weights_path = os.path.join("data", config.OBJECT_WEIGHTS_TINY)

            names_path = os.path.join("data", config.OBJECT_NAMES)
            
            if os.path.exists(config_path) and os.path.exists(weights_path) and os.path.exists(names_path):
                print(f"Loading YOLO Model from {weights_path}")
                self.net = cv2.dnn.readNet(weights_path, config_path)
                
                # Load names
                with open(names_path, "r") as f:
                    self.classes = [line.strip() for line in f.readlines()]
                config.OBJECT_CLASSES = self.classes # Update config for reference
                
                self.layer_names = self.net.getLayerNames()
                try:
                    self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
                except TypeError:
                    # Fix for different OpenCV versions
                    self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
            else:
                 print("Object model files (YOLO) not found. Disabling object detection.")
                 self.enabled = False

    def detect(self, frame):
        """Returns list of (class_name, confidence, box)"""
        if not self.enabled or self.net is None:
            return []
        
        height, width, channels = frame.shape
        
        # YOLO Preprocessing
        # Increased to 608x608 for better accuracy
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (608, 608), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)
        
        class_ids = []
        confidences = []
        boxes = []
        
        # Parse Outputs
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Non-Max Suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.3)
        
        results = []
        if len(indexes) > 0:
            for i in indexes.flatten():
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                box = boxes[i] # [x, y, w, h]
                results.append((label, confidence, tuple(box)))
        
        return results

class FaceDetector:
    def __init__(self):
        self.use_cuda = False
        self.cascade_path = os.path.join("data", config.HAAR_CASCADE_FILENAME)
        
        # Load CPU Cascade
        self.cpu_cascade = cv2.CascadeClassifier(self.cascade_path)
        if self.cpu_cascade.empty():
            print(f"Error: Could not load Haar cascade from {self.cascade_path}")
        
        # Check for CUDA/GPU support
        self.cuda_cascade = None
        self.gpu_available = False
        self.check_cuda()

        # Sub-detectors
        self.gender_detector = GenderDetector()
        self.object_detector = ObjectDetector()

    def check_cuda(self):
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
            if count > 0:
                self.gpu_available = True
                try:
                    self.cuda_cascade = cv2.cuda.CascadeClassifier(self.cascade_path)
                except Exception:
                    self.gpu_available = False
        except AttributeError:
            self.gpu_available = False

    def set_mode(self, use_gpu):
        if use_gpu and self.gpu_available and self.cuda_cascade:
            self.use_cuda = True
        else:
            self.use_cuda = False
            if use_gpu:
                print("Warning: GPU mode requested but not available. Falling back to CPU.")
        return self.use_cuda

    def detect(self, frame):
        """
        Detect faces, gender, and objects.
        Returns: 
           faces: list of (x, y, w, h, gender_label)
           objects: list of (label, confidence, (x,y,w,h))
           latency: ms
        """
        start_time = time.time()
        faces_rects = []
        
        # 1. Face Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.use_cuda and self.cuda_cascade:
            try:
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(gray)
                cuda_faces = self.cuda_cascade.detectMultiScale(gpu_frame)
                objects = cuda_faces.download() 
                if objects is not None:
                    faces_rects = objects[0]
            except Exception as e:
                print(f"GPU Error: {e}")
                faces_rects = self.cpu_cascade.detectMultiScale(
                    gray, config.SCALE_FACTOR, config.MIN_NEIGHBORS, minSize=config.MIN_SIZE
                )
        else:
            faces_rects = self.cpu_cascade.detectMultiScale(
                gray, config.SCALE_FACTOR, config.MIN_NEIGHBORS, minSize=config.MIN_SIZE
            )

        # 2. Gender Detection (on detected faces)
        faces_data = [] # List of (rect, gender_label)
        for (x, y, w, h) in faces_rects:
            # Padding
            padding = 10
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(frame.shape[1], x + w + padding)
            y2 = min(frame.shape[0], y + h + padding)
            
            face_img = frame[y1:y2, x1:x2]
            # Skip if too small
            if face_img.size > 0 and w > 20 and h > 20: 
                gender = self.gender_detector.predict_gender(face_img)
            else:
                 gender = "Unknown"
            faces_data.append(((x, y, w, h), gender))

        # 3. Object Detection (YOLO)
        objects_data = self.object_detector.detect(frame)

        end_time = time.time()
        latency = (end_time - start_time) * 1000 
        
        return {
            'faces': faces_data, 
            'objects': objects_data
        }, latency
