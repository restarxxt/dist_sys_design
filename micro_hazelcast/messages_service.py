from flask import Flask

app = Flask(__name__)

@app.route('/messages', methods=['GET'])
def static_message():
    return "Not implemented yet"

if __name__ == '__main__':
    app.run(port=5004)