import tkinter as tk
print("Imported tkinter")
try:
    root = tk.Tk()
    print("Created root")
    root.destroy()
    print("Destroyed root")
except Exception as e:
    print(f"Error: {e}")
