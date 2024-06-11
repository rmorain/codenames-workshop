import requests
from time import sleep

r = requests.get('https://api.github.com/events')
print(r.status_code)
print(r.text[:100],"...")

#makeHint returns hint,extra

DELAY = 2 #is this needed for socketio???

print("Ctrl-C to exit")
while True:
    sleep(DELAY)