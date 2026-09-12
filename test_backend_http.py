import requests
import time

print("Testing direct backend request via localhost:8000")
try:
    start = time.time()
    res = requests.get('http://127.0.0.1:8000/api/patients/PAT-001', timeout=5)
    print("GET /api/patients/PAT-001 status:", res.status_code)
    print(res.text[:200])

    res2 = requests.post('http://127.0.0.1:8000/api/patients', json={"name": {"full": "Test"}, "gender": "male", "age": 20, "weight": 70}, timeout=5)
    print("POST /api/patients status:", res2.status_code)
    print(res2.text[:200])
except Exception as e:
    print("Exception:", e)
