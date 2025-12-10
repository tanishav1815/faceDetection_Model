import cv2
import shutil
import os
import subprocess
import config

def download_file_curl(url, filepath):
    if os.path.exists(filepath):
        # check size > 0
        if os.path.getsize(filepath) > 0:
            print(f"File already exists: {filepath}")
            return
        else:
            print(f"File exists but empty, re-downloading: {filepath}")
            os.remove(filepath)

    print(f"Downloading {url} to {filepath}...")
    try:
        # -L follows redirects, -o writes to file
        subprocess.run(["curl", "-L", url, "-o", filepath], check=True)
        print("Download complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url}: {e}")
    except FileNotFoundError:
        print("Error: curl command not found. Please install curl.")

def setup():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Haar Cascade
    src = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    dst = 'data/haarcascade_frontalface_default.xml'
    
    if os.path.exists(src):
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print(f"Successfully copied {src} to {dst}")
    else:
        print(f"Error: Could not find Haar cascade at {src}")

    # Gender Models (Retry with curl)
    download_file_curl(config.GENDER_MODEL_URLS["gender_proto"], os.path.join("data", config.GENDER_PROTO))
    download_file_curl(config.GENDER_MODEL_URLS["gender_model"], os.path.join("data", config.GENDER_MODEL))

    # YOLO Models
    # Tiny
    download_file_curl(config.OBJECT_MODEL_URL_CONFIG_TINY, os.path.join("data", config.OBJECT_CONFIG_TINY))
    download_file_curl(config.OBJECT_MODEL_URL_WEIGHTS_TINY, os.path.join("data", config.OBJECT_WEIGHTS_TINY))
    
    # Full (Only if enabled or just download both to be safe? Let's download both)
    print("Downloading Full YOLOv4 models (This might take a while, ~245MB)...")
    download_file_curl(config.OBJECT_MODEL_URL_CONFIG_FULL, os.path.join("data", config.OBJECT_CONFIG_FULL))
    download_file_curl(config.OBJECT_MODEL_URL_WEIGHTS_FULL, os.path.join("data", config.OBJECT_WEIGHTS_FULL))
    
    download_file_curl(config.OBJECT_MODEL_URL_NAMES, os.path.join("data", config.OBJECT_NAMES))

if __name__ == "__main__":
    setup()
