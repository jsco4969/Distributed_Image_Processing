# worker.py
from flask import Flask, request, jsonify
import base64
from PIL import Image
import io

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_image():
    # Retrieve the image data and format from the request
    data = request.json
    image_data = data['image_data']
    format = data['format']

    # Decode the base64 image data
    image_binary = base64.b64decode(image_data)
    
    # Load the image for processing
    image = Image.open(io.BytesIO(image_binary))

    # Apply a simple filter (e.g., convert to grayscale)
    processed_image = image.convert('L')

    # Save the processed image to a binary stream
    img_byte_arr = io.BytesIO()
    processed_image.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)

    # Encode the processed image back to base64
    processed_image_data = base64.b64encode(img_byte_arr.read()).decode('utf-8')

    # Return the processed image as a JSON response
    return jsonify({'processed_image': processed_image_data})

if __name__ == '__main__':
    # Run the worker node on port 5001
    app.run(host='0.0.0.0', port=5001)
