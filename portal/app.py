from fastapi import FastAPI, UploadFile, File
import requests
import uuid
import json

app = FastAPI()

# REPLACE THESE WITH YOUR ACTUAL DETAILS
GITHUB_TOKEN = "your_personal_access_token_here"
GITHUB_USER = "your_github_username"
GITHUB_REPO = "portfolio-paas"

@app.post("/one-click-deploy")
async def start_deploy(file: UploadFile = File(...)):
    student_data = await file.read()

    # Generate a random 8-character ID for the bucket
    student_id = str(uuid.uuid4())[:8] 

    # Fire the signal to GitHub Actions
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "event_type": "deploy_trigger",
        "client_payload": {
            "id": student_id,
            "data": student_data.decode("utf-8")
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 204:
        return {"status": "Deployment Started!", "live_url": f"http://portfolio-{student_id}.s3-website-us-east-1.amazonaws.com"}
    else:
        return {"error": "Failed to trigger pipeline", "details": response.text}