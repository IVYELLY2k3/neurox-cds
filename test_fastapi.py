from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/test1")
def test1(data: dict):
    return data

client = TestClient(app)

print(client.post("/test1", json={"foo": "bar"}).json())
