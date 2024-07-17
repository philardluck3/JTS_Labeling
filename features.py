from Metadata import prep_metadata
from Object import object_dectect
from OCR import basic_ocr
from constants import MODEL_OBJECT_DETECTED_PATH
import os
import gc
import psutil

# get_memory_usage 
def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 ** 2)  # cConvert bytes to MB


def main_process_image(image_path):
    # Process an image file and extract metadata, objects, location, model of pictured device, datetime, and OCR.
    try:

        model_objects_path = MODEL_OBJECT_DETECTED_PATH
        image_name = os.path.basename(image_path)
        json_output = {image_name: {}}

        if image_name.lower().endswith((".jpg", ".jpeg", ".png", ".heic")):
            # Extract metadata
            model, date_time, latitude_decimal, longitude_decimal = prep_metadata(image_path)
            
            # Detect objects and OCR
            objects = object_dectect(image_path, model_objects_path)
            ocr_text = basic_ocr(image_path)

            output = {
                'objects': objects,
                'location': f'{latitude_decimal}, {longitude_decimal}',
                'model': model,
                'datetime': date_time,
                'ocr': ocr_text
            }
            
            json_output[image_name] = output

            # Clear memory
            del output, objects, ocr_text
            gc.collect()
            
        return json_output

    except Exception as e:
        print(f"An error occurred while processing {image_path}: {e}")
        return None