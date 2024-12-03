import zmq
import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION SECTION ---
# Specify the port this worker will bind to. Each worker needs a unique port.
port = os.getenv('PORT', '5555')  # Replace with your worker's port if not set via environment variable

# --- ZeroMQ SETUP ---
context = zmq.Context()
socket = context.socket(zmq.REP)
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
    executor.submit(process_image)
