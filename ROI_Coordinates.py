import cv2
import numpy as np

def select_roi(image):
    """Allow the user to select a region of interest (ROI)."""
    roi = cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")
    x, y, w, h = roi
    return int(x), int(y), int(x + w), int(y + h)

def main():
    # Open the camera
    camera = cv2.VideoCapture(0)  # Change device index if needed
    if not camera.isOpened():
        print("Error: Camera not found.")
        return

    print("Press 'q' to quit the live feed.")
    roi = None

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Unable to read from camera.")
            break
        
        # Show the live feed
        cv2.imshow("Live Feed", frame)

        # Press 'r' to select ROI
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            roi = select_roi(frame)
            print(f"Selected ROI: {roi}")        
        # Press 'q' to quit
        if key == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
