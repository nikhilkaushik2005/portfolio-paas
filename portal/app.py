from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import requests
import uuid
import os
import json
import boto3

app = FastAPI()

# --- Tell FastAPI where the HTML file is ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_ui():
    return FileResponse("static/index.html")

# --- ENVIRONMENT VARIABLES ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
GITHUB_USER = "nikhilkaushik2005"
GITHUB_REPO = "portfolio-paas"

# IMPORTANT: You must create this single bucket manually in AWS to hold all images
GLOBAL_ASSETS_BUCKET = os.getenv("AWS_ASSETS_BUCKET", "your-central-assets-bucket-name") 

# Initialize S3 Client (Ensure Render has AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY env vars)
s3_client = boto3.client('s3', region_name='us-east-1')

@app.post("/one-click-deploy")
async def start_deploy(
    json_data: str = Form(...), 
    images: Optional[List[UploadFile]] = File(None)
):
    # 1. Generate the unique ID
    student_id = str(uuid.uuid4())[:8] 
    
    # 2. Parse the JSON data sent from the frontend
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format payload")

    uploaded_urls = {}

    # 3. Intercept and Upload Images to the Central S3 Bucket
    if images:
        for img in images:
            if img.filename:
                # Store images in folders organized by student_id to prevent naming collisions
                s3_key = f"assets/{student_id}/{img.filename}"
                try:
                    s3_client.upload_fileobj(
                        img.file, 
                        GLOBAL_ASSETS_BUCKET, 
                        s3_key,
                        ExtraArgs={'ContentType': img.content_type}
                    )
                    # Map the local filename to the live AWS URL
                    uploaded_urls[img.filename] = f"https://{GLOBAL_ASSETS_BUCKET}.s3.amazonaws.com/{s3_key}"
                except Exception as e:
                    print(f"AWS Upload Error for {img.filename}: {str(e)}")

    # 4. Swap local filenames with Live AWS URLs inside the JSON payload
    for project in data.get('projects', []):
        live_image_links = []
        for filename in project.get('images', []):
            if filename in uploaded_urls:
                live_image_links.append(uploaded_urls[filename])
        
        # Overwrite the project's image list
        project['images'] = live_image_links

    # 5. Fire the signal to GitHub Actions with the UPDATED JSON
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "event_type": "deploy_trigger",
        "client_payload": {
            "id": student_id,
            "data": json.dumps(data) # <--- This now contains live image URLs!
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 204:
        return {
            "status": "Deployment Started!", 
            "live_url": f"http://portfolio-{student_id}.s3-website-us-east-1.amazonaws.com"
        }
    else:
        return {"error": "Failed to trigger pipeline", "details": response.text}