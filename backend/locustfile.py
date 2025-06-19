# from locust import HttpUser, task, between
# import json

# class JWTLoginUser(HttpUser):
#     wait_time = between(5, 10)
#     host = "http://192.168.2.108:8000/"  # Django API server

#     def on_start(self):
#         self.token = None
#         self.login()

#     @task
#     def login(self):
#         payload = {
#             "email": "urmish.cyblance@gmail.com",
#             "password": "123456789"
#         }

#         response = self.client.post("/api/login/", data=json.dumps(payload), headers={
#             "Content-Type": "application/json"
#         })

#         if response.status_code == 200:
#             data = response.json()
#             print(data)
#             print("✅ Login successful")
#         else:
#             print(f"❌ Login failed: {response.status_code}, {response.text}")


from locust import User, task, between, events
from websocket import create_connection, WebSocketConnectionClosedException
import time
import json
import random

class WebSocketBidUser(User):
    wait_time = between(1, 3)
    lot_id = 13  # Replace with your test lot ID

    def on_start(self):
        ws_url = f"ws://192.168.2.108:8000/ws/lot/{self.lot_id}/"
        try:
            self.ws = create_connection(ws_url)
            print("✅ WebSocket connected")
        except Exception as e:
            self.ws = None
            events.request.fire(
                request_type="WebSocket",
                name="connect",
                response_time=0,
                response_length=0,
                exception=e
            )

    def on_stop(self):
        if self.ws:
            self.ws.close()
            print("🔌 WebSocket connection closed")

    @task
    def place_bid(self):
        if not self.ws:
            return

        try:
            bid_amount = round(random.uniform(100, 500), 2)
            user_id = random.randint(1, 100)

            payload = {
                "type": "place_bid",
                "data": {
                    "amount": bid_amount,
                    "user_id": user_id,
                    "lot_id": self.lot_id
                }
            }

            start_time = time.time()
            self.ws.send(json.dumps(payload))

            response = self.ws.recv()  # Optional read back
            total_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type="WebSocket",
                name="place_bid",
                response_time=total_time,
                response_length=len(response),
                exception=None
            )

        except WebSocketConnectionClosedException as e:
            events.request.fire(
                request_type="WebSocket",
                name="place_bid",
                response_time=0,
                response_length=0,
                exception=e
            )
        except Exception as e:
            events.request.fire(
                request_type="WebSocket",
                name="place_bid",
                response_time=0,
                response_length=0,
                exception=e
            )
