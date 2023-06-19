import requests

headers = {
    'Authorization': 'Token c4f39339c02f9daa3174bd81c0da6407fdea94e0'
}
res = requests.get('http://127.0.0.1:8000/api/opportunities/', headers=headers)

print(res.content)
print(type(res.content))
print(res.status_code)