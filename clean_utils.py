import re
from PIL import Image, ImageDraw, ImageChops
import numpy as np
import cv2
import logging
from skimage.filters import try_all_threshold, threshold_minimum

# preprocess box input to help tesseract
def clean_box(image):
    # deal with text on dark background
    def adaptative_invert(image):
        image_copy = np.array(image).astype('uint8')
        hist = cv2.calcHist([image_copy],[0],None,[2],[0,256])
        if hist[0][0] > hist[1][0]:     # if more dark pixel (dark background), we invert image
            return ImageChops.invert(image_copy)
        return image_copy

    # apply threshold minimum to deal with background with lot of information (text outside of bubble)
    def apply_threshold_min(image):
        image_copy = np.array(image)
        _, threshold_image = cv2.threshold(image_copy, threshold_minimum(image_copy), 255, cv2.THRESH_BINARY)
        return Image.fromarray(threshold_image)

    # apply threshold minimum to deal with background with lot of information (text outside of bubble)
    def apply_threshold_adapt(image):
        #image_copy = cv2.GaussianBlur(image_copy,(5,5),0)
        _, threshold_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return Image.fromarray(threshold_image)

    # dilate then erode
    def dilation_erode(image):
        #copy
        image_copy = np.array(image)
        # kernel
        kernel = np.ones((7, 7), np.uint8)
        # dilate then erode
        image_copy = cv2.erode(image_copy, kernel, iterations=1)
        image_copy = cv2.dilate(image_copy, kernel, iterations=1)
        return Image.fromarray(image_copy)

    # attempt to substract background
    def substract_bg(image):
        # copy
        image_copy = np.array(image)
        # dilate then blur
        kernel = np.ones((3, 3), np.uint8)
        image_bg = cv2.dilate(image_copy, kernel, iterations=5)
        image_bg = cv2.blur(image_copy, (7,7))
        # substract the attempted background extraction
        image_copy = 255 - cv2.absdiff(image_copy, image_bg)
        # normalize
        cv2.normalize(image_copy, image_copy, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return Image.fromarray(image_copy)

    # apply all techniques
    new_image = adaptative_invert(image)
    #new_image = apply_threshold_min(new_image)
    new_image = apply_threshold_adapt(new_image)
    #new_image = dilation_erode(new_image)
    #new_image = substract_bg(new_image)
    return new_image

# preprocess tesseract output to remove undesired characters, spaces and linebreaks
def clean_tesseract(text):
    undesired = [" ", "\n\x0c", "\n"]
    clean_text = re.sub("|".join(undesired), "", text)
    return clean_text
