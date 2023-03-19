import hazelcast

queue_name = "my-bounded-queue"

hz = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        "192.168.192.145:5702",
        "192.168.192.145:5703"
    ],
)
queue = hz.get_queue(queue_name).blocking()
'''
for i in range(100):
    queue.put(i)
    print("Producing " + str(i))
queue.put(-1)
print("Producer finished")

'''
while True:
    item = queue.take()
    print("Consumed " + str(item))
    if (item == -1):
        queue.put(-1)
        break

