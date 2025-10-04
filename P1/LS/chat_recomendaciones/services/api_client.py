
import requests

class APIClientInterface:
    def send_message(self, url, payload):
        raise NotImplementedError("Debe implementar send_message")


class RequestsAPIClient(APIClientInterface):
    def send_message(self, url, payload):
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
