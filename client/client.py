import requests
from time import sleep
from sys import argv

r = requests.get('https://api.github.com/events')
print(r.status_code)
print(r.text[:100],"...")

#cnai.makeHint returns hint,extra

DELAY = 2 #is this needed for socketio???

print("Ctrl-C to exit")
while True:
    sleep(DELAY)

#run from command line: give code and team, then it plays the whole game :)
#client should run until game over, then terminate

USAGE = "Usage: <game code> <'red' | 'blue'>"
if __name__ == "__main__":
    if len(argv) < 3:
        print(USAGE)
        exit(1)
    code = argv[1]
    team = argv[2].lower()
    if team not in ['red', 'blue']:
        print(USAGE)
        exit(1)
    