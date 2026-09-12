import requests

print("Testing GET /api/patients")
try:
    res = requests.get('http://127.0.0.1:8000/api/patients', timeout=5)
    print("status:", res.status_code)
    print(res.text[:500])
except Exception as e:
    print("Exception:", e)
