from flask import Flask, request, abort, jsonify
import requests, json, argparse
import uuid
import random
import hazelcast
import consul, os

app = Flask(__name__)

consul_host = "192.168.1.105"
consul_port = 8500
consul_client = consul.Consul(host=consul_host, port=consul_port)

def get_service_address(service_name):
    _, services = consul_client.catalog.service(service_name)
    if services:
        address = services[0]['ServiceAddress']
        port = services[0]['ServicePort']
        return f"http://{address}:{port}"
    else:
        raise Exception(f"Service '{service_name}' not found in Consul.")

def get_hazelcast_settings():
    _, settings = consul_client.kv.get("hazelcast_settings")
    if settings:
        return json.loads(settings['Value'])
    else:
        raise Exception("Hazelcast settings not found in Consul.")

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


logging_service_address = get_service_address("logging-service")
messages_service_address = get_service_address("messages-service")
hazelcast_settings = get_hazelcast_settings()
message_queue_settings = get_message_queue_settings()

hz = hazelcast.HazelcastClient()
queue_name = message_queue_settings["queue_name"]
queue = hz.get_queue(queue_name).blocking()
i = 0
msg_array = []

@app.route("/", methods=["POST", "GET"])
def handle_request():
    global i
    if request.method == "POST":
        i+=1
        print(i)
        if i==11:
            return "Message not sent", 400
        _msg = request.form.get("msg")
        if not _msg:
            return "Message not provided", 400
        _id = str(uuid.uuid4())
        data = {"id": _id, "msg": _msg}
        logging_service = f"{logging_service_address}/logging"
        print(logging_service)
        response = requests.post(logging_service, data=data)
        queue.offer(json.dumps(_msg))
        return jsonify({"id": _id, "msg": _msg}), 200
    elif request.method == "GET":
        i = 0
        log_response = requests.get(f"{logging_service_address}/logging")
        msg_response = requests.get(f"{messages_service_address}/messages")
        if msg_response.text not in msg_array:
            msg_array.append(str(msg_response.text))
        return str([log_response.text, str(msg_array)]), 200
    else:
        abort(400)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    #register_service("facade-service", args.port)
    app.run(port=args.port)
