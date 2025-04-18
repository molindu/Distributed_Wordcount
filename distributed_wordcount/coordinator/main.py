import string
import os
import time
import httpx
import fitz  # for .pdf
from docx import Document  # for .docx
from fastapi import FastAPI, BackgroundTasks, Request
from typing import List, Dict
from sidecar import Sidecar

app = FastAPI()
sidecar = Sidecar("Coordinator")

# Store node info
registered_nodes = {
    "proposers": [],
    "acceptors": [],
    "learner": None
}

# -------------------------
# Registration & Health
# -------------------------

@app.get("/")
def health_check():
    return {"status": "Coordinator is up"}

@app.post("/register")
def register_node(info: Dict):
    node_type = info.get("type")
    address = info.get("address")

    if node_type == "proposer":
        registered_nodes["proposers"].append(address)
    elif node_type == "acceptor":
        registered_nodes["acceptors"].append(address)
    elif node_type == "learner":
        registered_nodes["learner"] = address
    else:
        return {"error": "Invalid node type"}

    sidecar.log(f"{node_type.capitalize()} registered: {address}")
    return {"message": f"{node_type.capitalize()} registered"}

# -------------------------
# Assign Letter Ranges
# -------------------------

def assign_letter_ranges():
    proposers = registered_nodes["proposers"]
    if not proposers:
        return []

    letters = list(string.ascii_lowercase)
    chunk_size = len(letters) // len(proposers)
    remainder = len(letters) % len(proposers)

    ranges = []
    start = 0

    for i in range(len(proposers)):
        end = start + chunk_size + (1 if i < remainder else 0)
        letter_range = letters[start:end]
        ranges.append({
            "proposer": proposers[i],
            "range": letter_range
        })
        start = end

    return ranges

@app.post("/start")
def start_processing(background_tasks: BackgroundTasks):
    background_tasks.add_task(distribute_letter_ranges)
    return {"message": "Started processing"}

def distribute_letter_ranges():
    ranges = assign_letter_ranges()
    for item in ranges:
        proposer = item["proposer"]
        data = {"range": item["range"]}
        try:
            httpx.post(f"{proposer}/assign_range", json=data)
            sidecar.log(f"Sent range {data} to proposer {proposer}")
        except Exception as e:
            sidecar.log(f"Failed to contact proposer {proposer}: {e}")

# -------------------------
# Document Processing
# -------------------------

@app.post("/process_file")
def process_file():
    filepath = "hello.docx"  # Change this to .txt or .docx if needed

    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    extension = os.path.splitext(filepath)[1].lower()

    try:
        if extension == ".txt":
            with open(filepath, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        send_line_to_proposers(line)
                        time.sleep(1)

        elif extension == ".docx":
            doc = Document(filepath)
            for para in doc.paragraphs:
                line = para.text.strip()
                if line:
                    send_line_to_proposers(line)
                    time.sleep(1)

        elif extension == ".pdf":
            doc = fitz.open(filepath)
            for page in doc:
                text = page.get_text()
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        send_line_to_proposers(line)
                        time.sleep(1)
        else:
            return {"error": "Unsupported file type. Use .txt, .docx, or .pdf"}

        return {"message": f"Processed {extension} file successfully."}

    except Exception as e:
        sidecar.log(f"Failed to read file: {e}")
        return {"error": str(e)}

def send_line_to_proposers(line):
    for proposer in registered_nodes["proposers"]:
        try:
            httpx.post(f"{proposer}/process_line", json={"line": line})
            sidecar.log(f"Sent line to {proposer}: {line}")
        except Exception as e:
            sidecar.log(f"Failed to send line to {proposer}: {e}")

# -------------------------
# Accessors for Learner/Acceptors
# -------------------------

@app.get("/learner")
def get_learner():
    return {"address": registered_nodes["learner"]}

@app.get("/acceptors")
def get_acceptors():
    return {"acceptors": registered_nodes["acceptors"]}

@app.get("/cluster_info")
def cluster_info():
    return {
        "total_proposers": len(registered_nodes["proposers"]),
        "total_acceptors": len(registered_nodes["acceptors"]),
        "learner_registered": registered_nodes["learner"] is not None
    }
