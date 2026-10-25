from flask import Flask, request, jsonify, render_template
from compatibility import compute_match_score
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")  
@app.route("/compare", methods=["POST"])
def compare():
    if 'your_csv' not in request.files or 'friend_csv' not in request.files:
        return jsonify({"error": "Both files required"}), 400

    file1 = request.files['your_csv']
    file2 = request.files['friend_csv']
    file1_path = os.path.join(UPLOAD_FOLDER, "user1.csv")
    file2_path = os.path.join(UPLOAD_FOLDER, "user2.csv")

    file1.save(file1_path)
    file2.save(file2_path)

    final_score, rating_score, genre_score = compute_match_score(file1_path, file2_path)

    return jsonify({
        "score": final_score,
        "details": {
            "rating_score": rating_score,
            "genre_score": genre_score
        }
    })

if __name__ == "__main__":
    app.run(debug=True)