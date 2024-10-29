# app.py
from flask import Flask, request, jsonify, send_file
import requests
import base64
import imghdr
import io

# Create a Flask application instance
app = Flask(__name__)

@app.route('/')
def index():
    # Serve the HTML file for the image upload interface
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Retrieve the uploaded image file from the request
    image_file = request.files['image']
    
    # Encode the image to base64 for transmission
    image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determine the format of the uploaded image
    original_format = imghdr.what(image_file)  
    
    # Send the image data to the master node for processing
    response = requests.post('http://master_address:port/process', json={'image_data': image_data, 'format': original_format})
    
    # Receive the processed image data from the master node
    processed_image_data = response.json()['processed_image']

    # Convert the processed image data back to binary
    processed_image_binary = base64.b64decode(processed_image_data)

    # Create an in-memory binary stream to send the processed image back to the user
    return send_file(io.BytesIO(processed_image_binary), mimetype=f'image/{original_format}', as_attachment=True, download_name=f'processed_image.{original_format}')

if __name__ == '__main__':
    # Run the Flask app on all available IP addresses on port 5000
    app.run(host='0.0.0.0', port=5000)

