import openai
import environ

env = environ.Env()
environ.Env.read_env()
API_KEY = env('AI_KEY')

openai.api_key = API_KEY

response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': '''You are a web scraper that takes a URL to a webpage that contains a list of opportunities
          and returns each opportunity and its details as a JSON object. 
            Each opportunity should have the following details: 
            title of the opportunity, the deadline for applying for the opportunity as a date, where the opportunity is located, the description
            of the opportunity, a URL linking to the page where someone can apply for the opportunity, 
            the type of opportunity chosen from this list (contest, residency, workshop, competition), and a list of keywords.'''},
    ]
)

print(response)