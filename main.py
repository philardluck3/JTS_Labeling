from fastapi import FastAPI, HTTPException, status, Header, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import  Optional, List
from constants import TOKEN, PORT, CACHE_TEXT_PATH, CACHE_OUT_PATH
import uvicorn
import json
import os

app = FastAPI()

# Create cache directory if it doesn't exist
os.makedirs("cache", exist_ok=True)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload-images/")
async def upload_image( images: List[UploadFile] = File(...),
                        key_ids: Optional[str] = Form(...),
                        token: Optional[str] = Header(...),
                        ):

    # Token validation
    if token != TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token invalid!")

    saved_files = []
    file_names = []

    # Ensure the directory exists
    os.makedirs("cache", exist_ok=True)

    for image in images:
        try:
            image_content = await image.read()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error reading file: {e}")

        image_path = f"cache/{image.filename}"
        _, ext = os.path.splitext(image_path)

        if ext.lower() in (".jpg", ".jpeg", ".png", ".heic"):
            try:
                with open(image_path, "wb") as f:
                    f.write(image_content)
                file_names.append(image.filename)
                saved_files.append({
                    "content_type": image.content_type,
                    "filename": image.filename,
                    "message": "Image uploaded successfully!"
                })
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=f"Error saving file: {e}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not accepted content type: {image.content_type}"
            )

    key_ids_list = key_ids.strip("[]").split(", ")
    key_ids_cleaned = [key.strip("'\"") for key in key_ids_list]

    if len(key_ids_cleaned) != len(file_names):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Mismatch between number of key IDs and images.")


    key_id_to_img = dict(zip(key_ids_cleaned, file_names))
    
    cacheText_path = CACHE_TEXT_PATH
    
    # Read existing data
    existing_data = []
    try:
        if os.path.exists(cacheText_path):
            with open(cacheText_path, "r") as file:
                existing_data = file.readlines()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error reading existing data: {e}")
    
    # Append new data and close file after writing
    try:
        with open(cacheText_path, "a") as file:
            for line in existing_data:
                file.write(line)
            
            for key_id, filename in key_id_to_img.items():
                storedata = f"{filename}, {key_id}"
                file.write(storedata + "\n")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error writing new data: {e}")
    
    return JSONResponse(content=saved_files, status_code=status.HTTP_200_OK)


@app.get("/result/{key_id}")
def get_text(key_id: str, token: Optional[str] = Header(...),):

    # Token validation
    if token != TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token invalid!")
    
    cache_out_path = CACHE_OUT_PATH
    content = {}
    if os.path.exists(cache_out_path):
        for filename in os.listdir(cache_out_path):
            if filename.lower().endswith('.txt'):
                key_id_cache_out, ext = os.path.splitext(filename)
                try:
                    if key_id[1:-1:] == key_id_cache_out :
                        content = {}
                        text_path = os.path.join(cache_out_path, filename)
                        with open(text_path, 'r') as file:
                            json_text = file.readlines()
                            content["filename"] = json_text[0].strip("\n")
                            json_correct = json_text[1].strip("\n").replace("'",'"')
                            content["attributes"] = json.loads(json_correct)
                except Exception as e :
                    raise print(f"Error reading existing data: {e}")
            else:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=f"Found invalid file-type")
    else:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=f"Path not found")
    
    if len(content) == 0 :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid key_id")
    
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
