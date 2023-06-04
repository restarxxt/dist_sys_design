import hazelcast
from flask import Flask, request, abort
import argparse, uuid, json
import subprocess
import signal
import consul
import os

app = Flask(__name__)

consul_host = "192.168.1.105"
consul_port = 8500
consul_client = consul.Consul(host=consul_host, port=consul_port)

def get_hazelcast_settings():
    _, settings = consul_client.kv.get("hazelcast_settings")
    if settings:
        return json.loads(settings['Value'])
    else:
        raise Exception("Hazelcast settings not found in Consul.")

def register_service(service_name, service_port):
    service_id = str(uuid.uuid4())
    service_ip = os.getenv('SERVICE_IP', 'localhost')
    consul_client.agent.service.register(
        service_name,
        service_id=service_id,
        address=service_ip,
        port=service_port
    )


hazelcast_settings = get_hazelcast_settings()

p = subprocess.Popen(['./start.sh'])
hz = hazelcast.HazelcastClient()
map_name = hazelcast_settings["map_name"]
messages = hz.get_map(map_name).blocking()
array = {}

@app.route("/logging", methods=["POST", "GET"])
def log_request():
    if request.method == "POST":
        _id = request.form['id']
        _msg = request.form['msg']
        messages.put(_id, _msg)
        print("Received message:", _msg)
        return "Success"
    elif request.method == "GET":
        keys = messages.key_set()
        for key in keys:
            value = messages.get(key)
            array[key] = value
        return array
    else:
        abort(400)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    #register_service("logging-service", args.port)

    try:
        app.run(port=args.port)
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
