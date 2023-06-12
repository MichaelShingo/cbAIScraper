import requests


res = requests.get('http://127.0.0.1:8000/api/opportunities/')

print(res.content)
print(type(res.content))
print(res.status_code)