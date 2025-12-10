import cv2
import numpy as np
import time

print("Imported cv2")
msg = np.zeros((200, 400, 3), dtype=np.uint8)
cv2.putText(msg, "Test", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

try:
    print("Attempting imshow")
    cv2.imshow("Test Window", msg)
    print("imshow returned, waiting for key")
    cv2.waitKey(100)
    print("waitKey returned")
    cv2.destroyAllWindows()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
