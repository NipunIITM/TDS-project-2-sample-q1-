import requests
import json

def test_api():
    try:
        # Make the POST request to our API
        response = requests.post('http://localhost:5000/api/')
        
        # Check if request was successful
        if response.status_code == 200:
            # Pretty print the JSON response
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))
            
            # Access individual answers
            answers = result['data']['answers']
            print("\nIndividual Answers:")
            print(f"1. Number of $2B movies before 2000: {answers['q1_movies_2bn_before_2000']}")
            print(f"2. Earliest $1.5B film: {answers['q2_earliest_1.5bn_film']}")
            print(f"3. Rank-Peak correlation: {answers['q3_rank_peak_correlation']}")
            print(f"4. Visualization is included as base64 string: {'q4_visualization' in answers}")
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the Flask server is running on port 5000.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    print("Testing API endpoint at http://localhost:5000/api/")
    test_api() 