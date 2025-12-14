import requests
import time

def test_grammar_agreement():
    url = "http://127.0.0.1:14300/check"
    # Test cases for Subject-Verb Agreement
    test_cases = [
        "He go to the store.",             # Expect: He goes...
        "She run fast.",                   # Expect: She runs...
        "They plays soccer.",              # Expect: They play...
        "I has a cat.",                    # Expect: I have...
        "The dog bark loudly.",            # Expect: The dog barks...
        "The dogs barks loudly."           # Expect: The dogs bark...
    ]
    
    print("Testing Subject-Verb Agreement...")
    
    for text in test_cases:
        try:
            response = requests.post(url, json={"text": text})
            if response.status_code == 200:
                result = response.json()
                print(f"\nInput:    {result['original_text']}")
                print(f"Output:   {result['corrected_text']}")
            else:
                print(f"Error for '{text}': {response.status_code}")
        except Exception as e:
            print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_grammar_agreement()
