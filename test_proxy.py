import requests

print("Testing via Vite proxy...")
try:
    res = requests.get('http://localhost:5173/api/patients')
    print(res.status_code, len(res.json()))
except Exception as e:
    print(e)
