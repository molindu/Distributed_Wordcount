from fastapi import FastAPI, Request
from sidecar import Sidecar
import requests
import os

# Dynamically get current port (default to 8002)
port = os.environ.get("PORT", "8002")
address = f"http://localhost:{port}"

app = FastAPI()
sidecar = Sidecar(f"Acceptor-{port}")
learner_address = None

@app.on_event("startup")
def register_with_coordinator():
    coordinator_url = "http://localhost:8000/register"
    info = {
        "type": "acceptor",
        "address": address  # Dynamic registration
    }
    try:
        requests.post(coordinator_url, json=info)
        sidecar.log(f"Registered with coordinator as {address}")
    except Exception as e:
        sidecar.log(f"Registration failed: {e}")

@app.post("/receive_counts")
async def receive_counts(request: Request):
    data = await request.json()
    sidecar.log(f"Received counts from proposer: {data}")
    forward_to_learner(data)
    return {"message": "Accepted"}

def forward_to_learner(data):
    global learner_address
    if learner_address is None:
        try:
            response = requests.get("http://localhost:8000/learner")
            learner_address = response.json().get("address")
            sidecar.log(f"Fetched learner address: {learner_address}")
        except Exception as e:
            sidecar.log(f"Failed to fetch learner address: {e}")
            return

    try:
        requests.post(f"{learner_address}/learn", json=data)
        sidecar.log(f"Forwarded data to learner: {data}")
    except Exception as e:
        sidecar.log(f"Failed to send to learner: {e}")
