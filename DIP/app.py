from flask import Flask, request, render_template, send_file
import cv2
import zmq
import numpy as np
import os

app = Flask(__name__)

# Initialize ZeroMQ context for dynamic worker connection
context = zmq.Context()

# Automatically detect available workers from environment variables or config
worker_ports = [5555, 5556, 5557, 5558]  # Example of four ports, adjust as necessary
worker_sockets = [context.socket(zmq.REQ) for _ in worker_ports]

# Connect each socket to its worker's port
for socket, port in zip(worker_sockets, worker_ports):
    socket.connect(f"tcp://localhost:{port}")

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
    app.run(debug=True, port=5000)
