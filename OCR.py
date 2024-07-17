import easyocr
import cv2
import numpy as np
from scipy.ndimage import rotate
import subprocess
from constants import OUTPUT_PNG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def convert_heic_to_png(heic_file, output_png):
    try:
        subprocess.run(['convert', heic_file, output_png], check=True)
        logging.info(f"Converted {heic_file} to {output_png}")
    except subprocess.CalledProcessError as e:

        logging.error(f"Error converting HEIC to PNG: {e}")
        return None
    return output_png

def preprocess_image(image_path):
    try:
        # Check if the file is HEIC and convert if necessary
        if image_path.lower().endswith(".heic"):
            output_png = OUTPUT_PNG
            image_path = convert_heic_to_png(image_path, output_png)
            if not image_path:
                return None

        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            logging.error(f"Error reading image: {image_path}")
            return None

        # Convert the image to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to segment the foreground text
        _, threshold_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Invert the thresholded image to make the text white on black background
        threshold_img = cv2.bitwise_not(threshold_img)

        # Skew Correction
        def find_score(arr, angle):
            data = rotate(arr, angle, reshape=False, order=0)
            hist = np.sum(data, axis=1)
            score = np.sum((hist[1:] - hist[:-1]) ** 2)
            return score

        delta = 1
        limit = 5
        angles = np.arange(-limit, limit + delta, delta)
        scores = [find_score(threshold_img, angle) for angle in angles]

        best_angle = angles[np.argmax(scores)]

        (h, w) = threshold_img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
        rotated_img = cv2.warpAffine(threshold_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Apply sharpening filter
        kernel_sharpening = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened_img = cv2.filter2D(rotated_img, -1, kernel_sharpening)

        # Create a 3x3 elliptical kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        # Apply dilation filter
        dilation = cv2.dilate(sharpened_img, kernel, iterations=1)

        return dilation
    except Exception as e:
        logging.error(f"Error in preprocessing image {image_path}: {e}")
        return None

def classify_ext(path):
    try:
        if path.lower().endswith('.heic'):
            output_png = OUTPUT_PNG
            path = convert_heic_to_png(path, output_png)
            if not path:
                raise Exception('HEIC conversion failed')
        return path
    except Exception as e:
        logging.error(f"Error in classifying extension for {path}: {e}")
        return None

def basic_ocr(image_path):
    try:
        image_path = classify_ext(image_path)
        filter_img = preprocess_image(image_path)
        if filter_img is None:
            raise Exception('Image preprocessing failed')

        reader = easyocr.Reader(['th', 'en'])
        result = reader.readtext(filter_img)
        text_str = ' '.join([text for (bbox, text, prob) in result if prob >= 0.2])
        return text_str
    
    except Exception as e:
        logging.error(f"Error in OCR process for {image_path}: {e}")

        return ''
