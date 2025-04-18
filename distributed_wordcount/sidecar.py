# sidecar.py
import httpx
import logging

logging.basicConfig(level=logging.INFO)

class Sidecar:
    def __init__(self, node_name):
        self.node_name = node_name

    def log(self, message):
        logging.info(f"[{self.node_name}] {message}")

    def send_post(self, url, data):
        try:
            response = httpx.post(url, json=data)
            self.log(f"Sent POST to {url}: {data}")
            return response
        except Exception as e:
            self.log(f"Failed to send POST to {url}: {e}")
