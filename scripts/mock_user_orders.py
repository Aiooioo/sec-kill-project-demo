import time
import random
from locust import HttpUser, task, between

API_PATH = "/purchase"

class User(HttpUser):
    wait_time = between(0.5, 2.5)

    host = "http://localhost:8000"

    def on_start(self):
        self.user_id = random.randint(0, 199)

        print(f"User {self.user_id} started session.")

    @task(1)
    def attempt_purchase(self):
        payload = {
            "product_id": random.randint(10000000, 10009999),
            "user_id": self.user_id,
            "amount": 1
        }

        with self.client.post(API_PATH, json=payload, catch_response=True, name=API_PATH) as response:
            try:
                if response.status_code == 200:
                    response.success()

                elif response.status_code == 400:
                    response.success()

                else:
                    response.failure(f"Unexpected status code: {response.status_code}")
                    print(f"User {self.user_id} ERROR! Status: {response.status_code}")

            except Exception as e:
                response.failure(f"Exception during request: {e}")
