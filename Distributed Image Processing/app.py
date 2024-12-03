from flask import Flask, request, render_template, send_file
import cv2
import zmq
import numpy as np
import os

app = Flask(__name__)

# --- CONFIGURATION SECTION ---
# Replace these with the actual public IPs of your worker machines and their open ports.
WORKER_ADDRESSES = [
    'tcp://73.251.223.221:5555',  # Replace IP of Worker 1
    'tcp://<Worker2_IP>:5556',  # Replace  of Worker 2
    'tcp://<Worker3_IP>:5557',  # Replace IP of Worker 3
]

# --- ZeroMQ SETUP ---
context = zmq.Context()
worker_sockets = [context.socket(zmq.REQ) for _ in WORKER_ADDRESSES]

# Connect each socket to its corresponding worker
for socket, address in zip(worker_sockets, WORKER_ADDRESSES):
    socket.connect(address)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Get uploaded file
    file = request.files['image']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    # Split the image into segments for each worker
    h, w, _ = img.shape
    num_workers = len(worker_sockets)
    h_unit = h // num_workers
    segments = [img[i * h_unit:(i + 1) * h_unit, :, :] for i in range(num_workers)]

    # Send each segment to a worker and collect results
    processed_segments = []
    for i, segment in enumerate(segments):
        worker_sockets[i].send_pyobj(segment)  # Send segment to worker
        processed_segment = worker_sockets[i].recv_pyobj()  # Receive processed segment
        processed_segments.append(cv2.cvtColor(processed_segment, cv2.COLOR_GRAY2BGR))

    # Combine processed segments back into a single image
    processed_image = np.vstack(processed_segments)
    cv2.imwrite("output.jpg", processed_image)

    # Send the final image to user for download
    return send_file("output.jpg", as_attachment=True)

if __name__ == '__main__':
    # Use 0.0.0.0 to allow connections from other devices on your network
    app.run(debug=True, host='0.0.0.0', port=5000)
