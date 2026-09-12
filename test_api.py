import requests

print("Testing get patient...")
res = requests.get('http://localhost:8000/api/patients/PAT-001')
print(res.status_code, res.text[:200])

print("Testing get patient history...")
res = requests.get('http://localhost:8000/api/patients/PAT-001/history')
print(res.status_code, res.text[:200])

print("Testing add patient...")
new_patient = {
    "name": {"given": "Alan", "family": "Renny", "full": "Alan Renny"},
    "gender": "male",
    "age": 20,
    "weight": 75,
    "height": 170,
    "bloodType": "A+",
    "contact": {"phone": "", "email": "", "emergencyContact": {"name": "", "relation": "", "phone": ""}}
}
res = requests.post('http://localhost:8000/api/patients', json=new_patient)
print(res.status_code, res.text[:200])

print("Testing get all patients...")
res = requests.get('http://localhost:8000/api/patients')
print(res.status_code, res.text[:200])
