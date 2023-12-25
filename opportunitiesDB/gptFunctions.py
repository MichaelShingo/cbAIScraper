import environ
import openai
import json
from .helperFunctions import findOppTypeTags, formatLocation, formatTitle

PROMPT_STANDARD = '''In the text below, I will provide a description of an opportunity. Based the description, do these 5 things? 
            1. Give me a comma-separated list of relevant keywords that musicians and artists might search for.
            2. If the description mentions an application fee or entry fee, write ONLY "Fee" in the description field. Do not write anything other than "Fee" in the description field. If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description using a minimum of 100 words. Include important requirements and any compensation as applicable.
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, full_state_name, country" as applicable. If you can't find a state or country, leave them out. If you can't find a definite location, write "None".
            4. Using less than 12 words, can you generate a title for this opportunity based on it's description? The title should read like a professional job listing. Include the name of the organization or person who posted the opportunity if possible.

            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","summary":"summary_text","location":"city, full_state_name, country","title":"title - organization_name"}
            '''


def get(title, description, prompt_type, location=''):
    prompt = ''
    if prompt_type == 'STANDARD':
        prompt = PROMPT_STANDARD

    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    openai.api_key = API_KEY

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': 'Location: ' + location +
             ' ' + prompt + '###' + title + '. ' + description},
        ]
    )

    print(response)
    print(type(response))
    print(response.choices)
    print(response.choices[0])

    completion_text = json.loads(str(response.choices[0]))  # returns DICT
    content = completion_text['message']['content']
    json_result = json.loads(content)

    return json_result


def format(json_result):
    # if json_result['location'] != 'None' else 'Online'
    res = {}
    location = json_result['location']
    for l in range(2):
        location = formatLocation(location)

    res['location'] = location

    if json_result['summary'] == 'Fee':
        res['fee'] = True  # increment fee in outer function
        return res
    elif json_result['summary'] != 'None':
        res['description'] = json_result['summary']
        res['fee'] = False

    if len(res['description']) < 40:
        res['continue'] = True
        return res
    else:
        res['continue'] = False

    res['titleAI'] = json_result['title']

    if json_result['keywords'].find(', ') != -1:
        res['keywordsList'] = json_result['keywords'].split(', ')
    else:
        res['keywordsList'] = json_result['keywords'].split(',')

    return res
