from app import app
import json

if __name__ == "__main__":
    print("Starting manual test...")
    client = app.test_client()
    
    # Test 1
    print("Sending request 1...")
    response = client.post('/api/chat', 
                       data=json.dumps({'message': 'ما هي تخصصات الماجستير؟'}),
                       content_type='application/json')
    
    print(f"Status Code: {response.status_code}")
    data = response.get_json()
    print(f"Response Body: {data}")
    
    if "MBA" in data['response'] and "القانون" in data['response']:
        print("Test passed! Found multiple programs.")
    else:
        print("Test failed! List might be incomplete.")
