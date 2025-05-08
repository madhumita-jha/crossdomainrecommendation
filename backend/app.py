from flask import Flask, request, jsonify
from recommendation import get_recommendations
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Cross-Domain Recommendation API is running!"})

@app.route('/recommend', methods=['GET'])
def recommend():
    movie = request.args.get('movie')
    if not movie:
        return jsonify({"error": "Please provide a movie name."}), 400
    
    try:
        recommendations = get_recommendations(movie)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
