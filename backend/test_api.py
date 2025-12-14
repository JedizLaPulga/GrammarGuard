import requests
import time

def test_backend():
    url = "http://127.0.0.1:14300/check"
    text = "the qick brown fox jumps over the the lazy dog."
    print(f"Sending text: '{text}'")
    
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
    # Wait a bit for server to start if we just ran it
    time.sleep(3) 
    test_backend()
