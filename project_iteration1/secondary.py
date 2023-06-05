import logging
from flask import Flask, request
import time

app = Flask(__name__)
replicated_messages = []

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_delay():
    start_time = time.perf_counter()
    end_time = start_time + 2
    
    while time.perf_counter() < end_time:
        pass

@app.route('/replicate', methods=['POST'])
def replicate_message():
    message = request.form.get('msg')
    if message:
        replicated_messages.append(message)
        logger.info(f"Message replicated: {message}")
        simulate_delay()
        #time.sleep(2)
        return "Message replicated"
    else:
        return "Invalid message", 400

@app.route('/messages', methods=['GET'])
def get_replicated_messages():
    return '\n'.join(replicated_messages)

app.run(host='0.0.0.0', port=25001)