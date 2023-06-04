from flask import Flask
import hazelcast
import json
import time
import argparse, uuid
import consul
import os

app = Flask(__name__)

consul_host = "192.168.1.105"
consul_port = 8500
consul_client = consul.Consul(host=consul_host, port=consul_port)

def get_message_queue_settings():
    _, settings = consul_client.kv.get("message_queue_settings")
    if settings:
        return json.loads(settings['Value'])
    else:
        raise Exception("Message Queue settings not found in Consul.")

def register_service(service_name, service_port):
    service_id = str(uuid.uuid4())
    service_ip = os.getenv('SERVICE_IP', 'localhost')
    consul_client.agent.service.register(
        service_name,
        service_id=service_id,
        address=service_ip,
        port=service_port
    )

message_queue_settings = get_message_queue_settings()

hz = hazelcast.HazelcastClient()

queue_name = message_queue_settings["queue_name"]
queue = hz.get_queue(queue_name).blocking()

messages = []

@app.route('/messages', methods=['GET'])
def get_messages():
    for i in range(0, 5):
        message = queue.take()
        print(message)
        if i == 4:
            break
        messages.append(message)
    return {"messages": messages}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    #register_service("messages-service", args.port)

    app.run(port=args.port)
