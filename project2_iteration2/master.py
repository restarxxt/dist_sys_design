from quart import Quart, request, jsonify
from uuid import uuid4
from aiohttp import ClientSession
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(name)

app = Quart(name)
messages = {}
SECONDARY_URLS = ['http://localhost:25001', 'http://localhost:25002']

async def post(url, data):
    async with ClientSession() as session:
        async with session.post(url, data=data) as response:
            return response.status == 200

async def run_asyncio_tasks(w, message, message_id):
    acks = [True]  # Master acknowledged
    async def replicate_message_to_secondaries():
        tasks = [post(f"{url}/replicate", {'msg': message, 'id': message_id}) for url in SECONDARY_URLS]
        if w > 1:  # Only wait for ACKs if w > 1
            for i, future in enumerate(asyncio.as_completed(tasks)):
                success = await future
                acks.append(success)
                if success:
                    logger.info(f"Message {message_id} replicated to {SECONDARY_URLS[i]}")
                else:
                    logger.error(f"Failed to replicate message {message_id} to {SECONDARY_URLS[i]}")
                if sum(acks) >= w:
                    break  # We have received 'w' ACKs, so we can stop waiting
        else:  # If w = 1, fire the tasks but don't await them
            for task in tasks:
                asyncio.create_task(task)

    await replicate_message_to_secondaries()
    return acks

@app.route('/messages', methods=['POST'])
async def append_message():
    message = (await request.get_json()).get('message')
    w = int((await request.get_json()).get('w', 1))
    logger.info(f"Message must be replicated {w} times")
    if message:
        message_id = str(uuid4())
        messages[message_id] = message
        acks = await run_asyncio_tasks(w, message, message_id)
        if sum(acks) >= w:
            logger.info(f"Received {w} ACKs for message {message_id}. Responding to client.")
            return "Message appended and replicated"
        else:
            logger.error("Replication failed")
            return "Replication failed", 500
    else:
        logger.error("Invalid message")
        return "Invalid message", 400

@app.route('/messages', methods=['GET'])
async def get_messages():
    return jsonify(messages)

loop = asyncio.get_event_loop()
app.run(loop=loop, host='0.0.0.0', port=25000)