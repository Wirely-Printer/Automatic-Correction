import cv2
import os
import time
import csv
from datetime import datetime
from octorest import OctoRest
import numpy as np

# Settings
image_capture_interval = 0.4  # Capture frequency in seconds
api_url = "http://localhost:5000"  # Replace with your OctoPrint URL
api_key = "5D60CE27902F4486AFD8112B24449923"  # Replace with your OctoPrint API Key
base_directory = "C:\\Users\\Charbel\\Desktop\\OctoRest\\Data"  # Base directory for storing folders

# Constants for image processing
CROP_SIZE = 320
FINAL_SIZE = 224
ROI = (207, 173, 274, 236)  # Example ROI (x_min, y_min, x_max, y_max)

# Ensure the base directory exists
os.makedirs(base_directory, exist_ok=True)

# Initialize OctoRest client
client = OctoRest(url=api_url, apikey=api_key)

# Function to determine the next folder name
def get_next_folder_name(base_directory):
    """Determine the next folder name based on the existing folders."""
    folders = [f for f in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, f)) and f.startswith("print")]
    if not folders:
        return "print0"  # Start with print0 if no folders exist
    latest_folder = max(folders, key=lambda x: int(x.replace("print", "")))
    next_folder_number = int(latest_folder.replace("print", "")) + 1
    return f"print{next_folder_number}"

# Get the output directory for this batch
batch_folder = get_next_folder_name(base_directory)
output_directory = os.path.join(base_directory, batch_folder)
os.makedirs(output_directory, exist_ok=True)

# CSV file name
csv_file = os.path.join(output_directory, f"{batch_folder}_data.csv")

# Initialize CSV file
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow([
            "img_path", "timestamp", "flow_rate", "feed_rate", "z_offset",
            "target_hotend", "hotend", "bed", "nozzle_tip_x", "nozzle_tip_y", "img_num", "print_id"
        ])

# Initialize the camera
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Camera not found.")
    exit()

# Function to process the image
def process_image(image, roi):
    """Apply ROI cropping, resizing, and rotating to the image."""
    x_min, y_min, x_max, y_max = roi
    cropped = image[y_min:y_max, x_min:x_max]
    cropped_resized = cv2.resize(cropped, (CROP_SIZE, CROP_SIZE), interpolation=cv2.INTER_CUBIC)
    rotated = cv2.rotate(cropped_resized, cv2.ROTATE_90_CLOCKWISE)
    final_resized = cv2.resize(rotated, (FINAL_SIZE, FINAL_SIZE), interpolation=cv2.INTER_CUBIC)
    normalized_image = final_resized / 255.0
    return normalized_image

# Function to retrieve OctoPrint data
def get_octoprint_data():
    """Retrieve real-time printer data from OctoPrint."""
    try:
        printer_info = client.printer()
        tool_temp = printer_info["temperature"]["tool0"]
        bed_temp = printer_info["temperature"]["bed"]

        # Placeholder for flow and feed rate; OctoRest lacks direct access to these
        flow_rate = 100
        feed_rate = 100

        # Placeholder for z_offset (OctoRest lacks direct access to this as well)
        z_offset = 0

        # Attempt to get print file name
        files_info = client.files()
        current_file = files_info["files"][0]["name"] if "files" in files_info and files_info["files"] else "unknown_file"

        return {
            "flow_rate": flow_rate,
            "feed_rate": feed_rate,
            "z_offset": z_offset,
            "target_hotend": tool_temp["target"],
            "hotend": tool_temp["actual"],
            "bed": bed_temp["actual"],
            "print_id": current_file
        }
    except Exception as e:
        print(f"Error retrieving OctoPrint data: {e}")
        return {
            "flow_rate": 100,
            "feed_rate": 100,
            "z_offset": 0,
            "target_hotend": 0,
            "hotend": 0,
            "bed": 0,
            "print_id": "unknown"
        }

# Capture images, process them, and update CSV in real-time
try:
    img_num = 0  # Initialize image numbering
    print(f"Starting image capture. Images and data will be saved in: {output_directory}. Press CTRL+C to stop manually.")
    while True:  # Replace with your stopping condition (e.g., while printer is printing)
        # Capture the image
        ret, frame = camera.read()
        if not ret:
            print("Error: Unable to capture image.")
            break

        # Process the captured image
        processed_image = process_image(frame, ROI)

        # Save the processed image
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = os.path.join(output_directory, f"image_{img_num}.jpg")
        cv2.imwrite(image_path, (processed_image * 255).astype(np.uint8))  # Convert back to uint8 for saving

        # Retrieve OctoPrint data
        octoprint_data = get_octoprint_data()

        # Combine image and OctoPrint data
        data = {
            "img_path": image_path,
            "timestamp": timestamp,
            "flow_rate": octoprint_data["flow_rate"],
            "feed_rate": octoprint_data["feed_rate"],
            "z_offset": octoprint_data["z_offset"],
            "target_hotend": octoprint_data["target_hotend"],
            "hotend": octoprint_data["hotend"],
            "bed": octoprint_data["bed"],
            "nozzle_tip_x": 531,  # Replace with actual nozzle tip coordinates if needed
            "nozzle_tip_y": 554,  # Replace with actual nozzle tip coordinates if needed
            "img_num": img_num,
            "print_id": octoprint_data["print_id"]
        }

        # Update CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data.values())

        print(f"Image {img_num} saved and metadata updated.")

        # Increment image number and wait for the next capture
        img_num += 1
        time.sleep(image_capture_interval)

except KeyboardInterrupt:
    print(f"Stopping image capture. All data saved in: {output_directory}.")

finally:
    # Release the camera
    camera.release()
