import requests

headers = {
    'Authorization': 'Token 5c738a4faa6ad5719886b230433efe1e4b4b8d4d'
}
res = requests.get('http://127.0.0.1:8000/api/opportunities/', headers=headers)

print(res.content)
print(type(res.content))
print(res.status_code)