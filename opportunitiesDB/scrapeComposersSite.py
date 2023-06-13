import requests, environ, openai, json
from bs4 import BeautifulSoup
from datetime import datetime
from .models import ActiveOpps
from .helperFunctions import tagToStr, findOppTypeTags

# Issues
        # can it filter out anything that has an application fee?
        # if it's missing certain fields, don't put it on the database at all? URL in particular

def scrape(prompt):
    OPP_LINK = 'http://live-composers.pantheonsite.io'
    PAGE_LINK = 'http://live-composers.pantheonsite.io/opps/results/taxonomy%3A13?page=' #pages start from 0
    NONE = 'None'

    #OPENAI SETUP
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    openai.api_key = API_KEY

    title = ''
    deadline = None
    location = '' 
    description = ''
    website = ''

    #SCRAPING ---------------------------------------------------------
    r = requests.get('http://live-composers.pantheonsite.io/opps/results/taxonomy%3A13')
    soup = BeautifulSoup(r.content, 'html.parser')
    opportunityRows = soup.select('.views-row .field-content a')
    oppLinks = [row['href'] for row in opportunityRows]
    maxPage = soup.select('.pager-last a')[0].attrs['href'][-1]

    for i in range(int(maxPage) + 1): #loops through all pages
        if i == 1: # REMOVE THIS IN FINAL VERSION
            break
        pageR = requests.get(PAGE_LINK + str(i))
        soup = BeautifulSoup(pageR.content, 'html.parser')
        opportunityRows = soup.select('.views-row .field-content a')
        oppLinks = [row['href'] for row in opportunityRows]
        k = 0 # FOR TESTING ONLY
        for oppLink in oppLinks: #loops through all opportunities on each page
            k += 1 # FOR TESTING ONLY
            if k == 3: # FOR TESTING ONLY
                break
            oppR = requests.get(OPP_LINK + oppLink)
            oppSoup = BeautifulSoup(oppR.content, 'html.parser')
            title = oppSoup.select('.views-field-title .field-content')[0].contents[0] if oppSoup.select('.views-field-title .field-content') else NONE
            descriptionTags = oppSoup.select('p') if oppSoup.select('p') else '' #TODO extra spaces are present here 
            descriptionList = []

            for tag in descriptionTags:
                for element in tag.contents: 
                    descriptionList.append(tagToStr(element))

            descriptionList.pop()
            description = '\n\n'.join(descriptionList)
            deadline = oppSoup.select('.date-display-single')[0].contents[0] if oppSoup.select('.date-display-single') else NONE

            if not deadline == NONE: # Dates must be YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format
                deadline += ' 23:59'
                deadline = datetime.strptime(deadline, '%d %b %Y %H:%M')
                deadline = datetime.strftime(deadline, '%Y-%m-%d %H:%M:59Z')

            website = oppSoup.select('.views-field-field-opp-url-url a')[0].contents[0] if oppSoup.select('.views-field-field-opp-url-url a') else OPP_LINK + oppLink
            
            # CHECK IF TITLE / DEADLINE IS ALREADY IN DATABASE, if True, continue
            if ActiveOpps.objects.filter(title=title, deadline=deadline).exists():
                print(f'title {title} already exists in database')
                continue

            # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'user', 'content': prompt + '###' + title + '. ' + description},
                ]
            )

            message = 'Successfully created all new entries.'

            try:
                completion_text = json.loads(str(response.choices[0])) # returns DICT
                content = completion_text['message']['content']
                print(f'json before json conversion = {content}')
                json_result = json.loads(content)
                location = json_result['location'] if json_result['location'] != 'None' else 'Online'
                # oppTypeList = (json_result['relevant_words']).split(', ') # GPT does not do well with finding oppTypes
                oppTypeList = findOppTypeTags(description.lower()) # Uses regular search function
                if json_result['summary'] != 'None':
                    description = json_result['summary']
                keywordsList = json_result['keywords'].split(', ')
                composerKeywords = ['composer', 'composition', 'new music']
                keywordsList.extend(composerKeywords)
                
                # CREATE A ACTIVEOPPS Model instance and save it to the database
                newModel = ActiveOpps(title=title, deadline=deadline,
                            location=location, description=description, link=website, 
                            typeOfOpp=oppTypeList, approved=False, keywords=keywordsList)
                newModel.save()
            except:
                print('An entry failed to be added.')
                message = 'At least 1 entry failed to be added.'
                continue

    return message