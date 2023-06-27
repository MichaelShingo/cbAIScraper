import openai, json, environ

def generate(description):
    TITLE_PROMPT = '''Using less than 12 words, can you generate a title for this opportunity based on it's description? 
                        The title should read like a professional job listing. Include the name of the organization or person who posted the opportunity if possible.
                        Format the result in JSON like this: {"title":"title - organization_name"}
                        '''
    
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    openai.api_key = API_KEY

    response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': TITLE_PROMPT + '###' + description},
                    ]
                )
    completion_text = json.loads(str(response.choices[0])) # returns DICT
    content = completion_text['message']['content']
    json_result = json.loads(content)
    title = json_result['title']
    return title 