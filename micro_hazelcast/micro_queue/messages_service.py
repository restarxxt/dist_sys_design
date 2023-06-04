from flask import Flask
import hazelcast
import json
import time
import argparse
import threading

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

hz = hazelcast.HazelcastClient()

queue_name = "message-queue"
queue = hz.get_queue(queue_name).blocking()

messages = []

@app.route('/messages', methods=['GET'])
def get_messages():
    for i in range(0,5):
        message = queue.take()
        print(message)
        if (i == 5):
    	    break
        messages.append(message)
    return {"messages": messages}

if __name__ == '__main__':
    app.run(port=args.port)
