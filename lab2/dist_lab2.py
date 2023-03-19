import hazelcast

map_name = "my-distributed-map"

def tasks_three_five():
    hz = hazelcast.HazelcastClient()
    key = 0
    counter = 0
    map = hz.get_map("my-distributed-map").blocking()
    for i in range(1000):
       	key+=1
        counter+=1
        map.put(key, counter)

def sixth_task_no_locks():
    hz = hazelcast.HazelcastClient()
    key = "No Locks"
    #counter = 0
    map = hz.get_map("my-distributed-map").blocking()
    #map.put(key, counter)
    if (map.contains_key(key) is False):
        map.put(key,0)
    for i in range(1000):
        counter = map.get(key)
        counter += 1
        map.put(key, counter)
    print(map.get(key))

def sixth_task_pessimistic():
	hz = hazelcast.HazelcastClient()
	key = "Pessimistic"
	map = hz.get_map("my-distributed-map").blocking()
	if (map.contains_key(key) is False):
		map.put(key,0)
	for i in range(1000):
		map.lock(key)
		try:
			value = map.get(key)
			value += 1
			map.put(key, value)
			#print(map.get(key))
		finally:
			map.unlock(key)
	print(map.get(key))

def sixth_task_optimistic():
    hz = hazelcast.HazelcastClient()
    key = "Optimistic"
    map = hz.get_map("my-distributed-map").blocking()
    if (map.contains_key(key) is False):
        map.put(key,0)
    loop = True
    for i in range(1000):
        while loop is not False:
            oldValue = map.get(key)
            newValue = oldValue
            newValue += 1
            if (map.replace_if_same(key, oldValue, newValue)): 
                break
    print(map.get(key))

if __name__ == "__main__":
	print("=======TASK 6c=======")
	#third_task()
	#sixth_task_no_locks()
	#sixth_task_pessimistic()
	sixth_task_optimistic()
