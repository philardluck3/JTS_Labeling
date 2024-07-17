from PIL import Image
import piexif

def dms_to_decimal(degree_tuple, minute_tuple, second_tuple, ref):
    
    degrees = degree_tuple[0] / degree_tuple[1]
    minutes = minute_tuple[0] / minute_tuple[1]
    seconds = second_tuple[0] / second_tuple[1]
    
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    
    return round(decimal_degrees, 6)

def extract_metadata(image_path):

    image = Image.open(image_path)
    exif_data = piexif.load(image.info['exif'])
    return exif_data

def prep_metadata(image_path):

    try:
        metadata = extract_metadata(image_path)
        all_attribute = {}
        
        for ifd in ('0th', 'Exif', 'GPS', '1st'):
            for tag in metadata[ifd]:
                name_f = piexif.TAGS[ifd][tag]['name']
                inf = metadata[ifd][tag]
                all_attribute[name_f] = inf

        model = all_attribute.get('Model', b'').decode()
        date_time = all_attribute.get('DateTime', b'').decode()

        lat_ref = all_attribute.get('GPSLatitudeRef', b'').decode()
        lat = all_attribute.get('GPSLatitude', [(0, 1), (0, 1), (0, 1)])
        longi_ref = all_attribute.get('GPSLongitudeRef', b'').decode()
        longi = all_attribute.get('GPSLongitude', [(0, 1), (0, 1), (0, 1)])
        
        latitude_decimal = dms_to_decimal(lat[0], lat[1], lat[2], lat_ref)
        longitude_decimal = dms_to_decimal(longi[0], longi[1], longi[2], longi_ref)

        return model, date_time, latitude_decimal, longitude_decimal

    except KeyError as e:
        print(f"Metadata key error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Default values in case of error
    return "Unknown Model", "Unknown DateTime", 0.0, 0.0
