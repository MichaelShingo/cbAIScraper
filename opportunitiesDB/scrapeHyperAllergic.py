from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, environ, openai, json
from .helperFunctions import findOppTypeTags
from .models import ActiveOpps

def scrape():
    PROMPT = '''In the text below, I will provide HTML containing information about an opportunity. Based the HTML, can you do these 6 things? 
            1. Extract the title.
            2. Extract the description. If the description mentions an application fee or entry fee, replace the description with "Fee".
            3. Extract the deadline date in the format MM/DD/YYYY. If there is no deadline listed, set the date to the last day of the current month.
            4. Extract the hyperlink linking to additional information.
            5. Based on the description, give me a comma-separated list of relevant keywords that artists might search for.
            6. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, state, country". If there is no state, leave it out. If you can't find a definite location, write "None". If the location contains a US state, write "United States" for country.
            Format the result as a JSON string like this:
            {"title":"Title of the Opportunity","description":"description of the opportunity","deadline":"MM/DD/YYYY","hyperlink":"url_to_website","keywords":"keyword1,keyword2,keyword3","location":"city, state, country"}
            '''

    # GET CURRENT MONTH URL
    url = ''
    indexPage = 'https://hyperallergic.com/tag/opportunities/'
    r = requests.get(indexPage)
    soup = BeautifulSoup(r.content, 'html.parser')
    entryTitles = soup.select('.entry-title a')
    today = datetime.today()
    curMonth = datetime.strftime(today, '%B')
    curYear = datetime.strftime(today, '%Y')
    for entryTitle in entryTitles:
        if entryTitle.text == f'Opportunities in {curMonth} {curYear}':
            url = entryTitle.attrs['href']
        
    #SCRAPING ---------------------------------------------------------
    print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    oppContainer = soup.select('#pico > p')

    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0
    
    for i in range(3, len(oppContainer)): # starts from the 3rd <p> tag to skip headings.
        try:
            title = ''
            deadline = '' #if none provided, use NONE
            location = '' #if none found, use ONLINE
            description = ''
            website = ''
            
            # OPEN AI SETUP
            env = environ.Env()
            environ.Env.read_env()
            API_KEY = env('AI_KEY')
            openai.api_key = API_KEY

            # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'user', 'content': PROMPT + '###' + str(oppContainer[i])},
                ]
            )

            completion_text = json.loads(str(response.choices[0])) # returns DICT
            content = completion_text['message']['content']
            print(f'json before json conversion = {content}')
            json_result = json.loads(content)
            location = json_result['location'] if json_result['location'] != 'None' else 'Online'

            description = json_result['description']
            if description == 'Fee':
                fee += 1
                continue
            oppTypeList = findOppTypeTags(description.lower()) # Uses regular search function
            location = json_result['location']
            if location.endswith(' None'):
                location = location[:-4]
            deadline = json_result['deadline']
            print(deadline, type(deadline))
            if deadline != 'None':
                deadline += ' 23:59'
                deadline = datetime.strptime(deadline, '%m/%d/%Y %H:%M')
            else:
                deadline = datetime.strftime(datetime.today() + timedelta(days=30))
            
            deadline = datetime.strftime(deadline, '%Y-%m-%d %H:%M:59Z')
            title = json_result['title']
            website = json_result['hyperlink']

            if ActiveOpps.objects.filter(title=title, deadline=deadline).exists():
                sameEntryCount += 1
                print(f'title {title} already exists in database')
                continue

            if json_result['keywords'].find(', ') != -1:
                keywordsList = json_result['keywords'].split(', ')
            else:
                keywordsList = json_result['keywords'].split(',')
            composerKeywords = ['composer', 'composition', 'new music']
            keywordsList.extend(composerKeywords)
            
            # CREATE A ACTIVEOPPS Model instance and save it to the database
            newModel = ActiveOpps(title=title, deadline=deadline,
                        location=location, description=description, link=website, 
                        typeOfOpp=oppTypeList, approved=True, keywords=keywordsList)
            newModel.save()
            successCount += 1
        
        except:
            failCount += 1
            print('An entry failed to be added.')
            continue
    
    message = {
        'website': 'HyperAllergic',
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'fee': str(fee)
    }

    return message

    
