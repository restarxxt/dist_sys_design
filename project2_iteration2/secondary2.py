from flask import Flask, request
import time

app = Flask(name)
replicated_messages = {}

def simulate_delay():
    time.sleep(5)  # Introduce a delay of 2 seconds

@app.route('/replicate', methods=['POST'])
def replicate_message():
    message = request.form.get('msg')
    message_id = request.form.get('id')
    if message and message_id and message_id not in replicated_messages:
        simulate_delay()  # Simulate delay
        replicated_messages[message_id] = message
        return "Message replicated", 200
    else:
        return "Invalid message", 400

@app.route('/messages', methods=['GET'])
def get_replicated_messages():
    return '\n'.join(replicated_messages.values())

app.run(host='0.0.0.0', port=25002)