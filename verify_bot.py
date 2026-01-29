import requests
import time

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

# Give server time to reload if needed
time.sleep(2)

print("\n--- Verifying Board of Trustees Names ---")

# Test 1: Board of Trustees
payload1 = {"message": "من هم اعضاء مجلس الامناء"}
print(f"\nQuery 1: {payload1['message']}")
try:
    response = requests.post(url, headers=headers, json=payload1)
    if response.status_code == 200:
        ans = response.json()['response']
        print("Answer:", ans)
        if "يعقوب ناصر الدين" in ans and "وليد أبو سلامة" in ans and "جبريل الخشمان" in ans:
            print("PASS: Board of Trustees names updated to Arabic.")
        else:
            print("FAIL: One or more names not found in Arabic.")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
