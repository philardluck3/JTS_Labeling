# README

## Project Overview

This project comprises two main scripts to manage image uploads, processing, and retrieval using FastAPI and Python. The application is designed to handle the following tasks:

1. **Upload images and associate them with key IDs.**
2. **Store image metadata and key ID mapping in a cache.**
3. **Retrieve processed results based on key IDs.**
4. **Process images using a multiprocessing approach.**

## Flowchart
![Project Logo](/image_for_git/POST_Method_1.png)

![Project Logo](/image_for_git/GET_Method_1.png)

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- TQDM
- Multiprocessing
- Easyocr
- Ultralytics : YOLOv8 - Detection (Open Image v7)
- Piexif : Metadata

## Tech Flowchart

![Project Logo](/image_for_git/Tech.png)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo.git
    cd your-repo
    ```

2. Install dependencies:
    ```bash
    python3 -m venv myprojectenv

    myprojectenv\Scripts\activate -> for windowns
    
    source myprojectenv/bin/activate -> for mac os

    pip3 install -r requirements.txt
    ```

3. Ensure the following directory structure exists:
    ```bash
    .
    ├── cache
    ├── cache_out   
    ├── constants.py
    ├── main.py
    ├── process_images.py
    └── features.py
    ```

4. Create a `constants.py` file with the following content:

    ```python
    
    # Model object detection path used in features.py
    MODEL_OBJECT_DETECTED_PATH = "path_to/yolov8m-oiv7.pt"
        
    # Cache path for temporary storage
    CAHCE_PATH = "path_to/cache"
    
    # Path to storedata.txt
    CACHE_TEXT_PATH = "path_to/cache/storedata.txt"
    
    # Output PNG path (this version does not support HEIC file -> this path does not use)
    OUTPUT_PNG = "path_to/cache/output.png"
    
    # Folder cache_out path
    CACHE_OUT_PATH = "path_to/cache_out"
    ```

    Remember to include the TOKEN and PORT for successful authentication!

## Running the Application

### FastAPI Server

The FastAPI server handles image uploads and retrieval.

1. **Start the FastAPI server:**
    ```bash
    run main.py 
    ```
   *Run FastAPI server in background*
    ```bash
    nohup python3 main.py > path_to/out_log.txt 2&1
    
    ```

2. **Endpoints:**
    - `GET /`: Returns a greeting message.
    - `POST /upload-images/`: Upload images with associated key IDs.
    - `GET /result/{key_id}`: Retrieve processed results based on key ID.

### Image Processing Script

This script processes the uploaded images using a multiprocessing approach.

1. **Run the image processing script:**
    ```bash
    python process_images.py
    ```

## File Descriptions

### `main.py`

The main FastAPI application:

- **Dependencies:**
  - `FastAPI`, `HTTPException`, `status`, `Header`, `File`, `UploadFile`, `Form`, `JSONResponse`
  - `os`, `json`, `Optional`, `List`
  - `uvicorn`
  - `TOKEN`, `PORT`,`CACHE_TEXT_PATH`, `CAHCE_OUT_PATH`  from `constants.py`

- **Endpoints:**
  - `GET /`: Returns a simple greeting.
  - `POST /upload-images/`: Uploads images, validates the token, and stores them in the cache directory.
  - `GET /result/{key_id}`: Retrieves processed results based on the key ID.

### `process_images.py`

The script for processing images:

- **Dependencies:**
  - `os`, `Pool`, `tqdm`
  - `CAHCE_PATH`, `CACHE_TEXT_PATH`, `CACHE_OUT_PATH` from `constants.py`
  - `main_process_image` from `features.py`

- **Functions:**
  - `write_cache_out(prep_data)`: Writes the processed image data to the cache output directory.
  - `remove_used_data()`: Removes used images and the storedata file.
  - `rearrange_format_output(model_output)`: Rearranges the output format of the processed images.
  - `main()`: Manages the multiprocessing of image processing.

## Example usage

### Prerequisites

1. Ensure you have set up your project environment and installed all dependencies as outlined in the README.
2. Ensure the FastAPI server is running.

### 1.Upload Images Example

1.1. **Start the FastAPI server:**

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

1.2 **Upload Images:**

Use a tool like Postman or cURL to send a `POST` request to `http://localhost:PORT/upload-images/`.

- **Endpoint:** `POST /upload-images/`
- **Headers:**
    - `token`: Your authentication token (`your_token`)
- **Form Data:**
    - `images`: Select multiple image files (e.g., image1.jpg, image2.png).
    - `key_ids`: A string containing key IDs associated with the images (e.g., `['id1', 'id2']`).

**Example with Postman:**

- Set the method to `POST`.
- Enter the URL `http://localhost:PORT/upload-images/`.
- In the Headers tab, add `token` with the value `your_token`.
- In the Body tab, select `form-data` and add:
    - Key: `images` (type: File), Value: Select multiple image files.
    - Key: `key_ids` (type: Text), Value: `['id1', 'id2']`.

**Example with cURL:**

```bash
    curl -X POST "http://localhost:PORT/upload-images/" \
         -H "token: your_token" \
         -F "images=@image1.jpg" \
         -F "images=@image2.png" \
         -F "key_ids=['id1', 'id2']"
```

**Expected Response:**

```json
    [
        {
            "content_type": "image/jpeg",
            "filename": "image1.jpg",
            "message": "Image uploaded successfully!"
        },
        {
            "content_type": "image/png",
            "filename": "image2.png",
            "message": "Image uploaded successfully!"
        }
    ]
```

### Retrieve Results Example

2. **Retrieve Results by Key ID:**

    Use a tool like Postman or cURL to send a `GET` request to `http://localhost:PORT/result/{key_id}`.

    - **Endpoint:** `GET /result/{key_id}`
    - **Headers:**
        - `token`: Your authentication token (`TOKEN`)

    **Example with Postman:**

    - Set the method to `GET`.
    - Enter the URL `http://localhost:PORT/result/id1`.
    - In the Headers tab, add `token` with the value `your_TOKEN`.

    **Example with cURL:**

    ```bash
    curl -X GET "http://localhost:PORT/result/id1" \
         -H "token: your_token"
    ```

    **Expected Response:**

    ```json
    {
        "filename": "image1.jpg",
        "attributes": {
            "attribute1": "value1",
            "attribute2": "value2",
            ...
        }
    }
    ```

### Full Workflow Example

1. **Start the FastAPI server:**

    ```bash
    uvicorn main:app --host 0.0.0.0 --port PORT --reload
    ```

2. **Upload Images and Key IDs:**

    ```bash
    curl -X POST "http://localhost:PORT/upload-images/" \
         -H "token: your_token" \
         -F "images=@image1.jpg" \
         -F "images=@image2.png" \
         -F "key_ids=['id1', 'id2']"
    ```

3. **Retrieve Results for a Key ID:**

    ```bash
    curl -X GET "http://localhost:PORT/result/id1" \
         -H "token: your_token"
    ```



## Notes

- Ensure the `CACHE_TEXT_PATH` and `CACHE_OUT_PATH` directories exist and are writable.
- The image processing function `main_process_image` should be defined in `features.py`.
- The token validation is a simple string comparison for demonstration purposes. Consider using a more secure method in production.

## Contact

For any inquiries, please contact [tted.phk@gmail.com].
