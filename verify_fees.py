import requests
import time

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

time.sleep(5)

# Test 1: Placement Test Fees (Generic/General)
payload1 = {"message": "كم رسم امتحان المستوى؟"}
print(f"\nQuery 1: {payload1['message']}")
try:
    response = requests.post(url, headers=headers, json=payload1)
    if response.status_code == 200:
        ans = response.json()['response']
        print("Answer:", ans)
        if "25" in ans or "25" in str(ans):
            print("PASS: Found 25 JOD for placement test.")
        else:
            print("FAIL: Did not find 25 JOD.")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Registration Fees for English
payload2 = {"message": "كم رسوم التسجيل الفصلية لتخصص اللغة الانجليزية؟"}
print(f"\nQuery 2: {payload2['message']}")
try:
    response = requests.post(url, headers=headers, json=payload2)
    if response.status_code == 200:
        ans = response.json()['response']
        print("Answer:", ans)
        if "500" in ans:
            print("PASS: Found 500 JOD for registration.")
        else:
            print("FAIL: Did not find 500 JOD.")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
