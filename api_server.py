from flask import Flask, jsonify
import json
from Scrape_data import fetch_and_parse_data, analyze_data

app = Flask(__name__)

@app.route('/api/', methods=['POST'])
def analyze():
    try:
        # Get the data and analyze it
        df = fetch_and_parse_data()
        result = analyze_data(df)
        
        # Parse the JSON string back into a list
        answers = json.loads(result)
        
        # Create the API response
        response = {
            "status": "success",
            "data": {
                "answers": {
                    "q1_movies_2bn_before_2000": answers[0],
                    "q2_earliest_1.5bn_film": answers[1],
                    "q3_rank_peak_correlation": answers[2],
                    "q4_visualization": answers[3]
                }
            },
            "error": None
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            "status": "error",
            "data": None,
            "error": str(e)
        }
        return jsonify(error_response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
