# sidecar.py
import logging
import requests

class Sidecar:
    def __init__(self, node_name):
        self.node_name = node_name
        logging.basicConfig(level=logging.INFO)

    def log(self, message):
        logging.info(f"[{self.node_name}] {message}")

    def send_post(self, url, data):
        try:
            response = requests.post(url, json=data)
            self.log(f"POST to {url} with data: {data}")
            return response
        except Exception as e:
            self.log(f"POST failed to {url}: {e}")
            return None
