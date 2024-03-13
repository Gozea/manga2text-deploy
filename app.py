import logging
from flask import Flask, jsonify
from flask import request as req
import json
from PIL import Image
from io import BytesIO

from detectntranslate import translate_from_image

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate() :
    logging.info('HTTP trigger function processed a request.')

    if check_file(req) == False:
        return jsonify({"response" :"POST must only contain images"})

    images = get_images(req)
    logging.info(f"Number of images to process : {len(images)}")
    translations = translate_from_image(images)

    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    return jsonify(translations)



"""
Checks if the file contains only images
-req : HttpRequest
"""
def check_file(req):
    # Ensure the request is a multipart/form-data request
    if not req.headers.get('Content-Type', '').startswith('multipart/form-data'):
        return False
    # Access uploaded files (if any)
    files = req.files
    if not files:
        return False
    # Check if uploaded files are images
    image_files = {}
    for name, file in files.items():
        if not file.content_type.startswith('image/'):
            return False
    return True


"""
Get images contained in request
-req : HttpRequest
"""
def get_images(req):
    images = []
    files = req.files
    for name, file in files.items():
        content = file.read()
        # Create a BytesIO object to treat binary data as a file-like object
        file_stream = BytesIO(content)
        # Open the image using PIL
        image = Image.open(file_stream)
        images.append((name, image))
    return images


if __name__ == "__main__":
    app.run(host='0.0.0.0')
