from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"pong": True})

@app.route("/soma", methods=["POST"])
def soma():
    data = request.json
    valor = data.get("valor", 0)
    return jsonify({"resultado": valor + 1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
