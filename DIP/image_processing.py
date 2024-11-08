import cv2
import numpy as np
import zmq
import multiprocessing

# Configuration
WORKER_ADDRESSES = ['tcp://localhost:5555', 'tcp://localhost:5556', 'tcp://localhost:5557', 'tcp://localhost:5558']
CHUNK_SIZE = 100  # Size of image chunks in pixels

# Split the image into chunks
def split_image(image_path):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    chunks = []
    
    for y in range(0, height, CHUNK_SIZE):
        for x in range(0, width, CHUNK_SIZE):
            chunk = image[y:y+CHUNK_SIZE, x:x+CHUNK_SIZE]
            chunks.append((chunk, (y, x)))  # (Image chunk, Position in original)
    
    return chunks, height, width

# Reassemble chunks into a full image
def reassemble_image(chunks, height, width):
    processed_image = np.zeros((height, width, 3), dtype=np.uint8)
    for chunk, (y, x) in chunks:
        processed_image[y:y+chunk.shape[0], x:x+chunk.shape[1]] = chunk
    return processed_image

# Distribute the image and collect processed chunks
def distribute_and_process_image(input_path, output_path):
    context = zmq.Context()
    sockets = [context.socket(zmq.REQ) for addr in WORKER_ADDRESSES]
    for sock, addr in zip(sockets, WORKER_ADDRESSES):
        sock.connect(addr)

    chunks, height, width = split_image(input_path)
    processed_chunks = []
    
    # Send chunks to workers
    for i, (chunk, pos) in enumerate(chunks):
        socket = sockets[i % len(WORKER_ADDRESSES)]
        socket.send_pyobj((chunk, pos))
    
    # Receive processed chunks
    for i in range(len(chunks)):
        socket = sockets[i % len(WORKER_ADDRESSES)]
        processed_chunks.append(socket.recv_pyobj())
    
    # Reassemble and save the final image
    final_image = reassemble_image(processed_chunks, height, width)
    cv2.imwrite(output_path, final_image)
