from fastapi import FastAPI, Request
from sidecar import Sidecar

app = FastAPI()
sidecar = Sidecar("Learner")

# Final result dictionary
final_counts = {}

@app.on_event("startup")
def register_with_coordinator():
    coordinator_url = "http://localhost:8000/register"
    info = {
        "type": "learner",
        "address": "http://localhost:8003"  # this learner's address
    }
    try:
        import requests
        requests.post(coordinator_url, json=info)
        sidecar.log("Registered with coordinator")
    except Exception as e:
        sidecar.log(f"Registration failed: {e}")
        
@app.post("/learn")
async def learn(request: Request):
    data = await request.json()
    sidecar.log(f"Received validated data: {data}")

    # Merge incoming data into final_counts
    for letter, words in data.items():
        if letter not in final_counts:
            final_counts[letter] = []
        final_counts[letter].extend(words)

    sidecar.log(f"Updated final counts: {final_counts}")
    return {"message": "Learned"}

@app.get("/result")
def get_result():
    return final_counts
