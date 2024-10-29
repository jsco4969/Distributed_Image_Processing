import base64
import requests

# Read the image file
with open('image.png', 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# Set the format of the image
format = 'PNG'  # or 'JPEG', 'JPG', etc.

# Define the master node URL
master_url = 'http://<master_node_address>:5000/process'

# Send the image for processing
response = requests.post(master_url, json={'image_data': image_data, 'format': format})

# Get the processed image data
processed_image_data = response.json()['processed_image']

# Decode the base64 data
processed_image_binary = base64.b64decode(processed_image_data)

# Save the processed image
with open('processed_image.png', 'wb') as processed_image_file:
    processed_image_file.write(processed_image_binary)

print('Processed image saved as processed_image.png')
