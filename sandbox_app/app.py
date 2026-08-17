from flask import Flask, request

app = Flask(__name__)

@app.route("/unit/search")
def search():
    name = request.args.get("name", "")
    return f"Searching for unit: {name}"

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)