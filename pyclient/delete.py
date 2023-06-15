import requests

res = requests.delete('http://127.0.0.1:8000/api/opportunities/delete/70/')

print(res.status_code)