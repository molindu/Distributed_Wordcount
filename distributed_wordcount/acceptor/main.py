from fastapi import FastAPI, Request
from sidecar import Sidecar
import requests

app = FastAPI()
sidecar = Sidecar("Acceptor")

# Learner address (will come from coordinator)
learner_address = None

@app.on_event("startup")
def register_with_coordinator():
    global learner_address
    coordinator_url = "http://localhost:8000/register"
    info = {
        "type": "acceptor",
        "address": "http://localhost:8002"  # this acceptor's address
    }
    try:
        requests.post(coordinator_url, json=info)
        sidecar.log("Registered with coordinator")
    except Exception as e:
        sidecar.log(f"Registration failed: {e}")


# 🔽 🔽 🔽 Add this endpoint here 🔽 🔽 🔽
@app.post("/receive_counts")
async def receive_counts(request: Request):
    data = await request.json()
    sidecar.log(f"Received counts from proposer: {data}")

    # Simulate validation (just forward to learner for now)
    forward_to_learner(data)

    return {"message": "Accepted"}


# 🔽 🔽 🔽 Add this helper function below it 🔽 🔽 🔽
def forward_to_learner(data):
    global learner_address
    if learner_address is None:
        try:
            response = requests.get("http://localhost:8000/learner")
            learner_address = response.json().get("address")
        except Exception as e:
            sidecar.log(f"Failed to fetch learner address: {e}")
            return

    try:
        requests.post(f"{learner_address}/learn", json=data)
        sidecar.log(f"Forwarded data to learner: {data}")
    except Exception as e:
        sidecar.log(f"Failed to send to learner: {e}")
