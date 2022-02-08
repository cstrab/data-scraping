from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/mentions')
def hello_world():
    data = [
        {
            "GME": {
                "mentions": 5,
                "sentiment": 0.5
            }
        },
        {
            "PLTR": {
                "mentions": 2,
                "sentiment": 0.9
            }
        },
    ]
    return jsonify(data)
