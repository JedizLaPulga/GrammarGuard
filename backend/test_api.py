import requests
import time

def test_backend():
    base_url = "http://127.0.0.1:14300"
    
    print("Checking health...")
    try:
        health = requests.get(f"{base_url}/health")
        print(f"Health Status: {health.status_code}")
        print("Health Response:", health.json())
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    url = f"{base_url}/check"
    text = "the qick brown fox jumps over the the lazy dog."
    print(f"\nSending text: '{text}'")
    
    try:
        response = requests.post(url, json={"text": text})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_backend()
