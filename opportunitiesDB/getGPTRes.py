from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import environ
import openai
import json
import csv
from .helperFunctions import findOppTypeTags, formatLocation, formatTitle


def getGPTRes():
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    openai.api_key = API_KEY

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': 'Location: ' + locationString +
             ' ' + PROMPT + '###' + title + '. ' + description},
        ]
    )

    completion_text = json.loads(str(response.choices[0]))  # returns DICT
    content = completion_text['message']['content']
    json_result = json.loads(content)
    # if json_result['location'] != 'None' else 'Online'
    location = json_result['location']
    for l in range(2):
        location = formatLocation(location)

    if json_result['summary'] == 'Fee':
        fee += 1
        # continue
    elif json_result['summary'] != 'None':
        description = json_result['summary']

    if len(description) < 40:
        # continue
        pass

    titleAI = json_result['title']

    if json_result['keywords'].find(', ') != -1:
        keywordsList = json_result['keywords'].split(', ')
    else:
        keywordsList = json_result['keywords'].split(',')
