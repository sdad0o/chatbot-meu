import requests
import time

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

# Give server time to reload if needed
time.sleep(2)

print("\n--- Verifying Content Updates ---")

# Test 1: International Programs
payload1 = {"message": "ما هي البرامج الدولية التي توفرها جامعة الشرق الاوسط"}
print(f"\nQuery 1: {payload1['message']}")
try:
    response = requests.post(url, headers=headers, json=payload1)
    if response.status_code == 200:
        ans = response.json()['response']
        print("Answer:", ans)
        if "MPharm ONLY" in ans and "بيدفوردشير" in ans:
            print("PASS: International Programs updated.")
        else:
            print("FAIL: International Programs mismatch.")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: President Name
payload2 = {"message": "من هو رئيس جامعة الشرق الأوسط؟"}
print(f"\nQuery 2: {payload2['message']}")
try:
    response = requests.post(url, headers=headers, json=payload2)
    if response.status_code == 200:
        ans = response.json()['response']
        print("Answer:", ans)
        if "سلام خالد المحادين" in ans:
            print("PASS: President name correct.")
        else:
            print("FAIL: President name mismatch.")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
