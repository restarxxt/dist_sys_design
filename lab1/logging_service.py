from flask import Flask, request

app = Flask(__name__)

messages = {}

@app.route("/logging", methods=["POST", "GET"])
def log_request():
    if request.method == "POST":
        _id = request.form['id']
        _msg = request.form['msg']
        messages[_id] = _msg
        print("Received message:", _msg)
        return "Success"
    elif request.method == "GET":
        return messages
    else:
        abort(400)

if __name__ == '__main__':
    app.run(port=5001)
