import requests

data = {
    'title': 'Test2',
    'deadline': '2020-10-08 09:33:37-0700',
    'location': 'Rotterdam, PA, United States',
    'description': 'This is merely a test to see if you want to apply.',
    'link': 'www.michaelshingo.com/portfolio',
    'typeOfOpp': ['grant', 'scholarship'],
    'approved': False,
    'keywords': ['test', 'application']

}

prod_url = 'https://web-production-022b.up.railway.app/api/opportunities/'
# res = requests.post('http://127.0.0.1:8000/api/opportunities/', data=data)
res = requests.post(prod_url, data=data)


print(res.content)
print(res.status_code)