
import requests
import time

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

print("\n--- Verifying Council of Deans ---")

# Give server time to reload
time.sleep(2)

query = "Who are the members of the Council of Deans?"
payload = {"message": query}

print(f"\nQuery: {query}")
try:
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        ans = response.json()['response']
        print("Answer:", ans)
        
        # Check for a few key names
        keywords = ["Salam Al-Mahadin", "Qusai Shambour", "Ayat Al Mughabi"]
        found_all = True
        for k in keywords:
            if k not in ans:
                print(f"MISSING: {k}")
                found_all = False
        
        if found_all:
            print("PASS: found key figures in response.")
        else:
            print("FAIL: Missing some figures.")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
