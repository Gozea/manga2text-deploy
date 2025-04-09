import os
import sys
import logging
from datetime import datetime

import numpy as np    # we're going to use numpy to process input and output data
import time
import cv2
from skimage.filters import try_all_threshold, threshold_minimum

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ultralytics import YOLO
import pytesseract

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from optimum.onnxruntime import ORTModelForSeq2SeqLM

from clean_utils import *

# Run the model on the backend
d=os.path.join(os.getcwd())
yolo_model= os.path.join(d, "yolov8n.onnx")
ja2en_model = "Gozear/jp2en"

# load model
yolo = YOLO(yolo_model, task='detect')
tessdata_dir = r'-l tesseract_ja_vert_fast+tesseract_ja_horz_fast --tessdata-dir "./"'
model_checkpoint = ja2en_model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
#model = ORTModelForSeq2SeqLM.from_pretrained(model_checkpoint)

# logging
if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

# predict boxes with YOLO
def predict_YOLO(image):
    # yolo
    predict_boxes = yolo(image)
    # crops
    boxes = []
    coordinates = []
    for box in predict_boxes[0].boxes.xyxy:
        # (coordinates, box)
        coord = box.cpu().numpy()
        boxes.append(image.crop(coord))
        coordinates.append(coord.tolist())
    return coordinates, boxes

# predict texts with tesseract
def predict_tesseract(boxes):
    # tesseract
    texts = []
    for box in boxes:
        texts.append(pytesseract.image_to_string(clean_box(box), config=tessdata_dir))
    #clean texts
    clean_texts = [clean_tesseract(text) for text in texts]
    return clean_texts

# predict translations with mBART
def predict_translation(texts):
    # translation
    tokenized_ja = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    out = model.generate(**tokenized_ja, max_new_tokens=40, decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"])
    translations = tokenizer.batch_decode(out, skip_special_tokens=True)
    return translations


def translate_from_image(images):
    responses = {}

    for name, image in images:
        # yolo boxes
        img = image.convert('L')
        start = time.time()
        yolo_coordinates, yolo_boxes = predict_YOLO(img)
        end = time.time()
        inference_time = np.round((end - start) * 1000, 2)
        logging.info(f'yolo time : {inference_time}')
        # tesseract texts
        start = time.time()
        tesseract_text = predict_tesseract(yolo_boxes)
        end = time.time()
        inference_time = np.round((end - start) * 1000, 2)
        logging.info(f'tesseract time : {inference_time}')
        # translations
        start = time.time()
        translations = predict_translation(tesseract_text)
        end = time.time()
        inference_time = np.round((end - start) * 1000, 2)
        logging.info(f'translation time : {inference_time}')
        # json
        resp = {
            'coordinates' : yolo_coordinates,
            'texts': tesseract_text,
            'translations': translations
        }
        responses[name] = resp

    logging.info(f'returning {responses}')
    return responses

if __name__ == '__main__':
    print(translate_from_image(sys.argv[1]))
