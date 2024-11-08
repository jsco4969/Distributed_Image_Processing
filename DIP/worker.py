import zmq
import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor

# Get the port number from the environment variable (or a default if not set)
port = os.getenv('PORT')
if not port:
    raise ValueError("No PORT environment variable set. Please set a unique port.")

# Initialize ZeroMQ context
context = zmq.Context()

# Create socket for this worker
socket = context.socket(zmq.REP)

# Bind to the specified port
socket.bind(f"tcp://*:{port}")
print(f"Worker listening on tcp://*:{port}")

# Define the image processing function
def process_image():
    while True:
        image_segment = socket.recv_pyobj()  # Receive image data from master
        gray_image_segment = cv2.cvtColor(image_segment, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        socket.send_pyobj(gray_image_segment)  # Send processed data back to master

# Start the image processing in a thread pool
with ThreadPoolExecutor(max_workers=1) as executor:
    executor.submit(process_image)  # Submit the process_image function for this worker
