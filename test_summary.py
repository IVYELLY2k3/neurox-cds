import sys
import os

# add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.patient_service import get_all_patients_summary

try:
    print("Testing get_all_patients_summary()...")
    res = get_all_patients_summary()
    print("Success!", len(res), "patients")
except Exception as e:
    import traceback
    traceback.print_exc()
