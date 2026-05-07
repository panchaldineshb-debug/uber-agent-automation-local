import requests
import os


class UberSkill:
    def __init__(self):
        self.token = os.getenv("UBER_SERVER_TOKEN")
        self.base_url = "https://sandbox-api.uber.com/v1.2"

    def request_ride(self, pickup_time, lat, long):
        endpoint = f"{self.base_url}/requests"
        payload = {
            "product_id": "a1111c8c-2222-3333-4444-555555555555",  # UberX Sandbox
            "start_latitude": lat,
            "start_longitude": long,
            "end_latitude": 40.523,  # Home Latitude
            "end_longitude": -74.343,  # Home Longitude
        }
        # In actual production, you'd use 'scheduled_rides' endpoint
        # For simple automation, we trigger the request at the time
        return requests.post(
            endpoint, json=payload, headers={"Authorization": f"Bearer {self.token}"}
        )

    def request_confirm(self, pickup_time, lat, long):
        # Your implementation here
        pass

    def request_cancel(self, request_id):
        # Your implementation here
        pass

    def request_message(self, request_id, message):
        # Your implementation here
        pass
