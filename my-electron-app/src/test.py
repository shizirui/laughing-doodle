import time
import json

data = {"message": "Hello from Python"}
while True:
    print(json.dumps(data))
    time.sleep(1)
