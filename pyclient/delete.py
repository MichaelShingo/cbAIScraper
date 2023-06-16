import requests

local_token = '5c738a4faa6ad5719886b230433efe1e4b4b8d4d'
cloud_token = 'c4f39339c02f9daa3174bd81c0da6407fdea94e0'
headers = {
    'Authorization': f'Token {local_token}'
}

resCloud = requests.delete('https://web-production-022b.up.railway.app/api/opportunities/delete/4', headers=headers)
# res = requests.delete('http://127.0.0.1:8000/api/opportunities/delete/70/', headers=headers)

print(resCloud)