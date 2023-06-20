"""
Created on Tue Jun 20 09:32:40 2023

@author: verpeutlab, david!
"""

import os
import time
import cv2
from PySpin import PySpin
import subprocess
import serial

# Set the save location for the videos (Edit this to correspond with where you want the videos saved!)
save_folder = "C:/Users/verpeutlab/Videos/pyspintest"

# Set the desired frames per second (This would be 120 in an ideal world, but Spinnaker is stubborn)
fps = 32

# Set the recording duration in seconds
recording_duration = 30

# Set the serial port and baud rate. Be sure to double check the serial port the Arduino is plugged into!
serial_port = "COM3"
baud_rate = 9600

# Initialize serial communication
ser = serial.Serial(serial_port, baud_rate)

# Wait for the "cr" signal from Arduino to start the recording. This may be slightly redundant, at least the corresponding code in the Arduino program. 
while ser.read(2) != b"cr":
    pass

# Initialize PySpin system
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()

if cam_list.GetSize() == 0:
    print("No cameras found.")
    system.ReleaseInstance()
    exit(1)

# Select the first camera
camera = cam_list.GetByIndex(0)

# Initialize camera
camera.Init()

# Configure camera settings
camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
camera.AcquisitionFrameRateEnable.SetValue(True)
camera.AcquisitionFrameRate.SetValue(fps)

# Start the camera stream
camera.BeginAcquisition()

# Create a VideoWriter object to save the recording
current_time = time.strftime("%Y%m%d_%H%M%S")
video_name = os.path.join(save_folder, f"pyspintest_recording_{current_time}.avi")

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*"MJPG")
video_writer = cv2.VideoWriter(video_name, fourcc, fps, (camera.Width.GetValue(), camera.Height.GetValue()))

# Record for the specified duration
start_time = time.time()
while time.time() - start_time < recording_duration:
    try:
        # Get the next image from the camera
        image_result = camera.GetNextImage()

        # Convert the image to a numpy array
        image_data = image_result.GetNDArray()

        # Convert the image to BGR format for compatibility with OpenCV
        image_bgr = cv2.cvtColor(image_data, cv2.COLOR_GRAY2BGR)

        # Write the image frame to the video file
        video_writer.write(image_bgr)

        # Release the image
        image_result.Release()

    except PySpin.SpinnakerException as e:
        print(f"Error: {e}")
        break

# Release the camera and system resources
camera.EndAcquisition()
camera.DeInit()
cam_list.Clear()
system.ReleaseInstance()

# Release the video writer
video_writer.release()

# Launch the video window using subprocess 
video_window = subprocess.Popen(["ffplay", "-i", video_name])

# Wait for the video window to close
video_window.wait()
