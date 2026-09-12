import requests
import time

print("Testing history endpoint")
try:
    res = requests.get('http://127.0.0.1:8000/api/patients/PAT-001/history', timeout=5)
    print("status:", res.status_code)
    print(res.text[:200])
except Exception as e:
    print("Exception:", e)
