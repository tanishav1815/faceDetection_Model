import os
import subprocess
import sys
import shutil

def build():
    print("🚀 Starting Build Process for Sentinel...")
    
    # Define platform specific separator for add-data
    # Linux/Mac = :
    # Windows = ;
    sep = ":" if os.name == 'posix' else ";"
    
    # Define paths
    data_src = "data"
    data_dst = "data"
    
    # Check if data exists
    if not os.path.exists(data_src):
        print(f"❌ Error: Data directory '{data_src}' not found. Run setup_data.py first.")
        return

    # PyInstaller Command
    # --onedir: Create a directory (faster to build/debug than --onefile)
    # --name: Name of the executable
    # --add-data: Include models/config
    # --clean: Clean cache
    # --noconsole: Hide terminal (Optional: Remove if you want to see logs)
    # Note: We keep console for now so user can see errors if any.
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--clean",
        "--name", "Sentinel",
        f"--add-data", f"{data_src}{sep}{data_dst}",
        "main.py"
    ]
    
    print(f"🔨 Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        
        # Manual Copy of Data (More robust than add-data)
        dist_data = os.path.join("dist", "Sentinel", "data")
        if os.path.exists(dist_data):
            shutil.rmtree(dist_data)
        shutil.copytree(data_src, dist_data)
        print(f"📦 Copied data folder to {dist_data}")

        print("\n✅ Build Complete!")
        print(f"📁 Output visible in: {os.path.abspath('dist/Sentinel')}")
        print("👉 You can zip this folder and share it.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build Failed: {e}")

if __name__ == "__main__":
    # Check if pyinstaller is installed
    if shutil.which("pyinstaller") is None:
        print("⚠️  PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    build()
