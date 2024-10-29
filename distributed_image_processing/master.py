from flask import Flask, request, jsonify
import base64
import threading
import requests
from PIL import Image
import io

app = Flask(__name__)

# List to hold worker node URLs
worker_nodes = ['http://worker1_address:port', 'http://worker2_address:port', 'http://worker3_address:port', 'http://worker4_address:port'] # Add more worker nodes as needed

@app.route('/process', methods=['POST'])
def process_image():
    data = request.json
    image_data = data['image_data']
    format = data['format']

    # Split the image into chunks
    image_chunks = split_image(image_data, format)

    processed_chunks = []

    # Use threading to process image chunks in parallel
    threads = []
    for i, chunk in enumerate(image_chunks):
        worker_url = worker_nodes[i % len(worker_nodes)]  # Cycle through available workers
        thread = threading.Thread(target=send_to_worker, args=(worker_url, chunk, format, processed_chunks))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Combine the processed chunks
    final_image = combine_chunks(processed_chunks, format)

    return jsonify({'processed_image': final_image})

def send_to_worker(worker_url, image_chunk, format, processed_chunks):
    response = requests.post(f'{worker_url}/process', json={'image_data': image_chunk, 'format': format})
    processed_image = response.json()['processed_image']
    processed_chunks.append(processed_image)

def split_image(image_data, format):
    # Decode the base64 image data
    image_binary = base64.b64decode(image_data)
    
    # Open the image using PIL
    image = Image.open(io.BytesIO(image_binary))
    
    # Define the number of chunks
    num_chunks = len(worker_nodes)
    
    # Calculate the width of each chunk
    chunk_width = image.width // num_chunks
    
    chunks = []
    for i in range(num_chunks):
        # Define the coordinates for each chunk
        left = i * chunk_width
        right = (i + 1) * chunk_width if i < num_chunks - 1 else image.width
        box = (left, 0, right, image.height)
        
        # Crop the image to create the chunk
        chunk = image.crop(box)
        
        # Save the chunk to a binary stream
        img_byte_arr = io.BytesIO()
        chunk.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        
        # Encode the chunk as base64
        chunk_data = base64.b64encode(img_byte_arr.read()).decode('utf-8')
        chunks.append(chunk_data)
    
    return chunks

def combine_chunks(chunks, format):
    # Decode the first chunk to determine the height and format
    first_chunk_binary = base64.b64decode(chunks[0])
    first_chunk = Image.open(io.BytesIO(first_chunk_binary))
    
    # Create a new image to hold the combined result
    combined_image = Image.new('RGB', (first_chunk.width * len(chunks), first_chunk.height))
    
    # Paste each chunk into the combined image
    for i, chunk_data in enumerate(chunks):
        chunk_binary = base64.b64decode(chunk_data)
        chunk = Image.open(io.BytesIO(chunk_binary))
        combined_image.paste(chunk, (i * chunk.width, 0))
    
    # Save the combined image to a binary stream
    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)
    
    # Encode the combined image as base64
    combined_image_data = base64.b64encode(img_byte_arr.read()).decode('utf-8')
    
    return combined_image_data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
