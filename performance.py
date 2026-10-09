import requests
import time

with open ("IPs.txt", "r") as file:
	ip_list = file.read().split()

ip_us = ip_list[0]
ip_eu = ip_list[1]

# Clear databases for testing
requests.post(f"http://{ip_us}:8080/clear")
requests.post(f"http://{ip_eu}:8080/clear")
# Sleep for 2 seconds to guarantee stability
time.sleep(2)

# Measure Latency of /register
reg_lat_us = []
reg_lat_eu = []

for i in range(10):
	us_start = time.time()
	requests.post(f"http://{ip_us}:8080/register", json={ "username": f"US_User{i}"})
	us_end = time.time()

	eu_start = time.time()
	requests.post(f"http://{ip_eu}:8080/register", json={ "username": f"EU_User{i}"})
	eu_end = time.time()

	reg_lat_us.append(us_end - us_start)
	reg_lat_eu.append(eu_end - eu_start)

print("Average latency of /register for US server: ", str(sum(reg_lat_us) / 10))
print("Average latency of /register for EU server: ", str(sum(reg_lat_eu) / 10))

# Measure Latency of /list
list_lat_us = []
list_lat_eu = []

for i in range(10):
    us_start = time.time()
    requests.get(f"http://{ip_us}:8080/list")
    us_end = time.time()

    eu_start = time.time()
    requests.get(f"http://{ip_eu}:8080/list")
    eu_end = time.time()

    list_lat_us.append(us_end - us_start)
    list_lat_eu.append(eu_end - eu_start)

print("Average latency of /list for US server: ", str(sum(list_lat_us) / 10))
print("Average latency of /list for EU server: ", str(sum(list_lat_eu) / 10))

# Observe Eventual Consistency
# The normal requests library is blocking until response, but we want to send GET while POST is in flight. nvm even with async its 0
import asyncio
import httpx

async def consistency_test():
	
	notfound = 0
	total_run = 0
	
	async with httpx.AsyncClient() as client:
		for i in range(100):
			username = f"ConsistencyTest{i}"
			post_task = client.post(f"http://{ip_us}:8080/register", json={"username": username})
			get_task = client.get(f"http://{ip_eu}:8080/list")
			_, get_res = await asyncio.gather(post_task, get_task)
			if username not in get_res.json()["users"]: notfound += 1
			total_run += 1

	return notfound, total_run

result, tot = asyncio.run(consistency_test())
print("Number of times user not found in other server immediately after registration: ", str(result), " out of ", str(tot))