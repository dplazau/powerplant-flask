from flask import Flask, request, render_template
from flask.json import jsonify
from src.handlers.payloadHandler import show_files, calculate

app = Flask(__name__)



@app.route(rule='/', methods=['GET'])
def home():
    return render_template('home.html', payloads = show_files())

@app.route(rule="/home", methods=['GET'])
def get_payloads_api():
    return jsonify(show_files())

@app.route(rule="/productionplan", methods=['POST'])
def post_api():
    return calculate(request.form)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8888)


