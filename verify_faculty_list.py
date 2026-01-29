import requests
import json
import time

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

# Wait for server to start
time.sleep(5)

# Test 2: Ask in Arabic about IT faculty
payload = {"message": "ما هي تخصصات كلية تكنولوجيا المعلومات؟"}
print(f"\nSending request: {payload['message']}")

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print("Response:", data['response'])
    
    # Check for presence of ALL 4 known IT majors
    expected_majors = ["علم الحاسوب", "الذكاء الإصطناعي", "هندسة البرمجيات", "الأمن السيبراني"]
    found_all = True
    for major in expected_majors:
        if major not in data['response']:
            print(f"MISSING: {major}")
            found_all = False
    
    if found_all:
        print("PASS: Found ALL IT majors.")
    else:
        print("FAIL: Missing some majors.")

except Exception as e:
    print(f"Error: {e}")
