from fastapi import FastAPI, Request
from sidecar import Sidecar
import requests

# Store acceptor addresses (will fetch from Coordinator)
acceptor_addresses = []

app = FastAPI()
sidecar = Sidecar("Proposer")
assigned_range = []

@app.on_event("startup")
def register_with_coordinator():
    # Change this if your coordinator runs on another IP/port
    coordinator_url = "http://localhost:8000/register"
    info = {
        "type": "proposer",
        "address": "http://localhost:8001"  # This proposer's address
    }
    try:
        requests.post(coordinator_url, json=info)
        sidecar.log("Registered with coordinator")
    except Exception as e:
        sidecar.log(f"Registration failed: {e}")

@app.post("/assign_range")
async def assign_range(request: Request):
    data = await request.json()
    global assigned_range
    assigned_range = [char.lower() for char in data.get("range", [])]  # <-- lowercase
    sidecar.log(f"Received letter range: {assigned_range}")
    return {"message": "Range assigned"}

@app.post("/process_line")
async def process_line(request: Request):
    data = await request.json()
    line = data.get("line", "")
    words = line.strip().split()
    result = {}

    for word in words:
        first_letter = word[0].lower()
        if first_letter in assigned_range:
            result.setdefault(first_letter, []).append(word)

    sidecar.log(f"Processed line: {line}")
    sidecar.log(f"Words counted: {result}")

    send_to_acceptors(result)

    return {"counts": result}

def send_to_acceptors(result):
    get_acceptor_addresses()
    for acceptor in acceptor_addresses:
        try:
            requests.post(f"{acceptor}/receive_counts", json=result)
            sidecar.log(f"Sent result to acceptor {acceptor}: {result}")
        except Exception as e:
            sidecar.log(f"Failed to send to acceptor {acceptor}: {e}")

def get_acceptor_addresses():
    global acceptor_addresses
    if acceptor_addresses:
        return acceptor_addresses

    try:
        response = requests.get("http://localhost:8000/acceptors")
        acceptor_addresses = response.json().get("acceptors", [])
        sidecar.log(f"Fetched acceptor addresses: {acceptor_addresses}")
    except Exception as e:
        sidecar.log(f"Failed to fetch acceptors: {e}")
