import requests
import time

print("Testing direct backend request via localhost:8000")
try:
    start = time.time()
    res = requests.get('http://localhost:8000/api/patients/PAT-001', timeout=2)
    print(res.status_code)
    print("Time taken:", time.time() - start)
except Exception as e:
    print(e)
