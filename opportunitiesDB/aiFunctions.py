import environ
import openai
import json
from .helperFunctions import tagToStr, findOppTypeTags, formatLocation, formatTitle


def getGPTResponse(content):
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    openai.api_key = API_KEY

    # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': content},
        ]
    )

    completion_text = json.loads(str(response.choices[0]))  # returns DICT
    content = completion_text['message']['content']
    json_result = json.loads(content)

    return json_result


def getAILocation(json_result):
    location = json_result['location'] if json_result['location'] != 'None' else 'Online'
    for l in range(2):
        location = formatLocation(location)
    return location


def checkDescriptionHasFee(description):
    return description == 'Fee' or description.endswith(
        'Fee') or description.startswith('Fee')


def getKeywordsList(json_result):
    keywordsList = []
    if json_result['keywords'].find(', ') != -1:
        keywordsList = json_result['keywords'].split(', ')
    else:
        keywordsList = json_result['keywords'].split(',')

    return keywordsList
