from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from Scrape_data import fetch_and_parse_data, analyze_data

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Health check endpoint for Render
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "API is running"
    })

@app.route('/api/', methods=['POST'])
def analyze():
    try:
        # Get the data and analyze it
        print("Fetching data from Wikipedia...")
        df = fetch_and_parse_data()
        
        if df is None:
            return jsonify({
                "status": "error",
                "data": None,
                "error": "Failed to fetch or parse data from Wikipedia"
            }), 500
            
        print("Analyzing data...")
        result = analyze_data(df)
        answers = json.loads(result)
        
        # Create response
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
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in API: {str(e)}")  # Log the error
        return jsonify({
            "status": "error",
            "data": None,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
