import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Test 1: Metformin + [Fever, Asthma] → should show diagnosis mismatch
data = json.dumps({
    "patientId": "PAT-001",
    "drugName": "Metformin",
    "dose": "500 mg",
    "diagnoses": ["Fever", "Asthma"]
}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/prescriptions/analyze",
    data=data,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
print("=== Test 1: Metformin + [Fever, Asthma] ===")
print(f"Total alerts: {result['totalAlerts']}")
for a in result["alerts"]:
    print(f"  [{a['severity']}] {a['title']}")
    print(f"    {a['message'][:100]}")
print()

# Test 2: Paracetamol + [Fever, Asthma, UTI] → should NOT show diagnosis mismatch
data2 = json.dumps({
    "patientId": "PAT-001",
    "drugName": "Paracetamol",
    "dose": "500 mg",
    "diagnoses": ["Fever", "Asthma", "UTI"]
}).encode()
req2 = urllib.request.Request(
    "http://localhost:8000/api/prescriptions/analyze",
    data=data2,
    headers={"Content-Type": "application/json"}
)
resp2 = urllib.request.urlopen(req2)
result2 = json.loads(resp2.read())
print("=== Test 2: Paracetamol + [Fever, Asthma, UTI] ===")
print(f"Total alerts: {result2['totalAlerts']}")
has_mismatch = any(a["id"].startswith("DMM-") for a in result2["alerts"])
print(f"Has diagnosis mismatch: {has_mismatch} (expected: False)")
for a in result2["alerts"]:
    print(f"  [{a['severity']}] {a['title']}")
print()

# Test 3: Salbutamol + [Asthma] → should NOT show mismatch (asthma medicine)
data3 = json.dumps({
    "patientId": "PAT-001",
    "drugName": "Salbutamol",
    "dose": "4 mg",
    "diagnoses": ["Asthma"]
}).encode()
req3 = urllib.request.Request(
    "http://localhost:8000/api/prescriptions/analyze",
    data=data3,
    headers={"Content-Type": "application/json"}
)
resp3 = urllib.request.urlopen(req3)
result3 = json.loads(resp3.read())
print("=== Test 3: Salbutamol + [Asthma] ===")
print(f"Total alerts: {result3['totalAlerts']}")
has_mismatch3 = any(a["id"].startswith("DMM-") for a in result3["alerts"])
print(f"Has diagnosis mismatch: {has_mismatch3} (expected: False)")
print()

print("All tests passed!" if not has_mismatch and not has_mismatch3 else "Some tests failed!")
