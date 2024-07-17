from constants import CAHCE_PATH, CACHE_TEXT_PATH, CACHE_OUT_PATH
from features import main_process_image  # Ensure that main_process_image can be pickled
from multiprocessing import Pool
from tqdm import tqdm
import os


def write_cache_out(prep_data):

    # Ensure the directory exists
    os.makedirs("cache", exist_ok=True)

    cacheText_path = CACHE_TEXT_PATH

    # Read existing data, read in storedata.txt
    existing_data = []
    try:
        if os.path.exists(cacheText_path):
            with open(cacheText_path, "r") as file:
                existing_data = file.readlines()
    except Exception as e:
        raise print(f"Error reading existing data: {e}")
    
    # Ensure the directory exists
    os.makedirs("cache_out", exist_ok=True)

    try:
        for line in existing_data:

            filename, key_id = line.strip("\n").split(', ')
            cache_out_path = CACHE_OUT_PATH

            try:

                if filename in prep_data:
                    out_text_path = os.path.join(cache_out_path, f"{key_id}.txt")

                    with open(out_text_path, "w") as file:
                        file.write(filename + '\n')
                        file.write(str(prep_data[filename]) + '\n')

            except ValueError as ve:
                print(f"Error processing line '{line}': {ve}")

    except Exception as e:
        raise Exception(f"Error reading line in write output process: {e}")

def remove_used_data():

    cacheText_path_1 = CACHE_TEXT_PATH
    cache_out_path = CACHE_OUT_PATH

    # Read existing data key_id in storedata.txt
    existing_data_1 = []

    try:

        if os.path.exists(cacheText_path_1):
            with open(cacheText_path_1, "r") as file:
                existing_data_1 = file.readlines()

    except Exception as e:
        raise print(f"Error reading existing data: {e}")
    
    dict_of_key_id_and_imagename = {}
    try:

        for line in existing_data_1:
            image_name, key_id = line.strip('\n').split(', ')
            dict_of_key_id_and_imagename[key_id] = image_name
            
    except Exception as e:
        raise print(f"Error reading existing data: {e}")
    
    #key_id in cache_out 
    cache_out_key_ids = []
    try:
        for text in os.listdir(cache_out_path):
            if text.lower().endswith(".txt"):
                cache_out_key_ids.append(text.split('.')[0])

    except Exception as e:
        raise Exception(f"Error : {e}")
    
    cache_out_key_ids.sort()
    
    n = 1  
    for key_id_cache in dict_of_key_id_and_imagename:

        if key_id_cache in cache_out_key_ids:
            folder_cache_path = CAHCE_PATH
            image_to_delete_path = os.path.join(folder_cache_path, dict_of_key_id_and_imagename[key_id_cache])
            os.remove(image_to_delete_path) # remove image
            n += 1

            if n == len(dict_of_key_id_and_imagename):
                os.remove(CACHE_TEXT_PATH)

        else:

            folder_cache_path = CAHCE_PATH
            image_path_collect = os.path.join(folder_cache_path, dict_of_key_id_and_imagename[key_id_cache])
            try: 

                if os.path.exist(image_path_collect):
                    exist_store_data = CACHE_TEXT_PATH
                    filename = dict_of_key_id_and_imagename[key_id_cache]
                    with open(exist_store_data, "a") :
                        storedata = f"{filename}, {key_id_cache}"
                        file.write(storedata + "\n")
                        
            except Exception as e :
                raise Exception(f"Error : {e}")
    return 

def rearrange_format_output(model_output) : 

    prep_data = {}
    for i in model_output:
        if i != None :
            k, v = list(i.items())[0]
            prep_data[str(k)] = v

    return prep_data
        

def main():
    folder_path = CAHCE_PATH
    task = main_process_image
    inputs = [os.path.join(folder_path, image_path) for image_path in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, image_path))]

    results = []
    def update_progress(result):
        results.append(result)
        pbar.update()
    with Pool(processes=8) as pool:
        with tqdm(total=len(inputs)) as pbar:
            try:
                for input_file in inputs:
                    pool.apply_async(task, args=(input_file,), callback=update_progress)
                pool.close()
                pool.join()
            except Exception as error:
                print(f"An error occurred: {error}")
    return results


if __name__ == "__main__":
    #run multiprocessing 8-core , output of main is list of dicts
    model_output = main()

    #rearrange_format_output rearrange format to "image_name" : attributes
    prep_data = rearrange_format_output(model_output) 

    #prepare data for receive get method
    write_cache_out(prep_data)

    #delete images and storedata.txt in cache 
    remove_used_data()


