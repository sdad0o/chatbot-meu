import requests
import concurrent.futures
import time
import json
import random

# Configuration
URL = "https://chatbot.meu.edu.jo/api/chat"
NUM_USERS = 50
MESSAGE = "مرحبا، ما هي التخصصات المتاحة؟"  # "Hello, what majors are available?"

def simulate_user(user_id):
    """Simulates a single user sending a message."""
    session_id = f"load_test_user_{user_id}"
    payload = {
        "message": MESSAGE,
        "session_id": session_id
    }
    
    start_time = time.time()
    try:
        response = requests.post(URL, json=payload, timeout=30)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            return {"status": "success", "duration": duration, "user_id": user_id, "code": 200}
        else:
            return {"status": "failure", "duration": duration, "user_id": user_id, "code": response.status_code, "error": response.text}
            
    except Exception as e:
        return {"status": "error", "duration": time.time() - start_time, "user_id": user_id, "error": str(e)}

def run_load_test():
    print(f"Starting load test with {NUM_USERS} concurrent users...")
    print(f"Target URL: {URL}")
    print("-" * 50)

    results = []
    start_total = time.time()
    
    # Use ThreadPoolExecutor to simulate concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        # Submit all tasks
        futures = [executor.submit(simulate_user, i) for i in range(NUM_USERS)]
        
        # Wait for all to complete
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    end_total = time.time()
    total_duration = end_total - start_total
    
    # Analysis
    success_count = sum(1 for r in results if r["status"] == "success")
    failure_count = sum(1 for r in results if r["status"] != "success")
    avg_time = sum(r["duration"] for r in results) / len(results) if results else 0
    max_time = max(r["duration"] for r in results) if results else 0
    min_time = min(r["duration"] for r in results) if results else 0

    print("-" * 50)
    print("LOAD TEST RESULTS")
    print("-" * 50)
    print(f"Total Requests: {NUM_USERS}")
    print(f"Success: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Total Test Duration: {total_duration:.2f} seconds")
    print(f"Average Response Time: {avg_time:.2f} seconds")
    print(f"Max Response Time: {max_time:.2f} seconds")
    print(f"Min Response Time: {min_time:.2f} seconds")
    print("-" * 50)
    
    if failure_count > 0:
        print("\nErrors encountered:")
        for r in results:
            if r["status"] != "success":
                print(f"User {r['user_id']}: {r.get('code', 'N/A')} - {r.get('error', 'Unknown error')}")

if __name__ == "__main__":
    run_load_test()
