
import requests
import time

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

print("\n--- Verifying Contact Information ---")

# Give server time to reload
time.sleep(2)

queries = [
    ("كيف يمكنني التواصل مع الجامعه", ["712", "4790222", "هاتف", "تواصل"]),
    ("ما رقم الجامعه", ["712", "4790222"]),
    ("ما عنوان الجامعه", ["طريق المطار", "جسر المطار"])
]

for q, expected_keywords in queries:
    print(f"\nQuery: {q}")
    try:
        response = requests.post(url, headers=headers, json={"message": q})
        if response.status_code == 200:
            ans = response.json()['response']
            print("Answer:", ans)
            
            found = any(k in ans for k in expected_keywords)
            if found:
                print("PASS")
            else:
                print(f"FAIL: Expected one of {expected_keywords}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
