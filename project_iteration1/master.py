import logging
from flask import Flask, request
import requests, os

app = Flask(__name__)
messages = []

SECONDARY_URLS = os.getenv('SECONDARY_URLS', '').split(',')
#SECONDARY_URLS = ['http://127.0.0.1:25001']

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/messages', methods=['POST'])
def append_message():
    message = request.form.get('msg')
    if message:
        messages.append(message)
        
        # Replicate the message on all secondaries
        acks = []
        for secondary_url in SECONDARY_URLS:
            replication_url = f"{secondary_url}/replicate"
            response = requests.post(replication_url, data={'msg': message})
            if response.status_code == 200:
                acks.append(True)
            else:
                acks.append(False)
        
        if all(acks):
            logger.info(f"Message appended and replicated: {message}")
            return "Message appended and replicated"
        else:
            logger.error("Replication failed")
            return "Replication failed", 500
    else:
        return "Invalid message", 400

@app.route('/messages', methods=['GET'])
def get_messages():
    return '\n'.join(messages)

app.run(host='0.0.0.0', port=25000)