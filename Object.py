from ultralytics import YOLO
from constants import OUTPUT_PNG
import json
import subprocess

def convert_heic_to_png(heic_file, output_png):
    try:
        subprocess.run(['convert', heic_file, output_png])
    except Exception as e:
        print(f"Error converting HEIC to PNG: {e}")

def object_dectect(path, model_path) :
    if path.lower().endswith((".heic")) :
        output_png = OUTPUT_PNG
        convert_heic_to_png(path, output_png)    
        path = output_png
    
    model = YOLO(model_path)
    results = model(path)
    results_json_from = results[0].tojson(normalize=False, decimals=5)
    results_list_from = json.loads(results_json_from)
    output = []
    for i in results_list_from :
        if i['confidence'] > 0.2 :
            del i['class']
            output.append(i)
    return output

