import requests
r = requests.get('https://api.github.com/events')
print(r.status_code)
print(r.text[:100],"...")