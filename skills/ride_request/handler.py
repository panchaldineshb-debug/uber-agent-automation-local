import requests
import keyring


class UberSkill:
    SERVICE_NAME = "SarabiLabs_Uber_Automator"

    def __init__(self):
        self.token = keyring.get_password(self.SERVICE_NAME, "uber_server_token")
        if self.token is None:
            raise RuntimeError("Keychain entry 'SarabiLabs_Uber_Automator/uber_server_token' not found. Run 'make seed-secrets'.")
        self.base_url = "https://sandbox-api.uber.com/v1.2"

    def request_ride(self, pickup_time, lat, long):
        endpoint = f"{self.base_url}/requests"
        payload = {
            "product_id": "a1111c8c-2222-3333-4444-555555555555",  # UberX Sandbox
            "start_latitude": lat,
            "start_longitude": long,
            "end_latitude": 40.523,  # Home Latitude
            "end_longitude": -74.343,  # Home Longitude
            "pickup_datetime": pickup_time.isoformat() + "+00:00"
        }
        # In actual production, you'd use 'scheduled_rides' endpoint
        # For simple automation, we trigger the request at the time
        response = requests.post(
            endpoint, json=payload, headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 201:
            print("✅ Ride requested successfully.")
            return True
        else:
            print(f"❌ Failed to request ride: {response.text}")
            return False

    def request_confirm(self, pickup_time, lat, long):
        raise NotImplementedError

    def request_cancel(self, request_id):
        raise NotImplementedError

    def request_message(self, request_id, message):
        raise NotImplementedError
