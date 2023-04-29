from flask import Flask, request, abort, jsonify
import requests, json
import uuid
import random

app = Flask(__name__)

messages_service = "http://localhost:5004/messages"

@app.route("/", methods=["POST", "GET"])
def handle_request():
    if request.method == "POST":
        _msg = request.form.get("msg")
        if not _msg:
            return "Message not provided", 400
        _id = str(uuid.uuid4())
        data = {"id": _id, "msg": _msg}
        port = random.randint(5001, 5003)
        logging_service = "http://localhost:{}/logging".format(port)
        response = requests.post(logging_service, data=data)
        return jsonify({"id": _id, "msg": _msg}), 200
    elif request.method == "GET":
        port = random.randint(5001, 5003)
        log_response = requests.get("http://localhost:{}/logging".format(port))
        print(log_response.text)
        msg_response = requests.get(messages_service)
        return str([log_response.text, msg_response.text]), 200
    else:
        abort(400)

if __name__ == "__main__":
    app.run(port=5000)
