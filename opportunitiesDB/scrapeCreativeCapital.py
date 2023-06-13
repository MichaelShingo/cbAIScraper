# Web scraper for Creative Capital, saves data in CSV file formatted for upload to Wix
#World cities list attribution - https://simplemaps.com/data/world-cities

import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, environ, openai, json
from .helperFunctions import findOppTypeTags
from .models import ActiveOpps


# ISSUES
    # How do you handle RateLimitError from ChatGPT? Wait and try again in a few minutes?

def scrape(prompt):
    PROMPT = '''In the text below, I will provide a description of an opportunity. Based the description, do these 2 things? 
            1. Give me a comma-separated list of relevant keywords that musicians and artists might search for.
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, state, country" as applicable. If there is no state, leave it out. If you can't find a definite location, write "None".
            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","location":"city, state, country"}
            '''
    NONE = 'None'
    APPROVED = 'FALSE'

    title = ''
    deadline = '' #if none provided, use NONE
    location = '' #if none found, use ONLINE
    description = ''
    website = ''

    # OPEN AI SETUP
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    API_KEY_SCRAPEOPS = env('API_KEY_SCRAPEOPS')
    openai.api_key = API_KEY

    #SCRAPING ---------------------------------------------------------
    today = datetime.today()
    curMonthStr = datetime.strftime(today, '%B')
    prevMonthNum = datetime.strftime(today - timedelta(days=30), '%m')
    nextMonthStr = datetime.strftime(today + timedelta(days=30), '%B')
    year = datetime.strftime(today, '%Y')
    for day in range(25, 32):
        urlVersion = f'https://creative-capital.org/{year}/{prevMonthNum}/{day}/artist-opportunities-{curMonthStr}-and-{nextMonthStr}-{year}/'
        r = requests.get(
            url='https://proxy.scrapeops.io/v1/',
            params={
                'api_key': API_KEY_SCRAPEOPS,
                'url': urlVersion, 
            })
        if 200 <= r.status_code < 300:
            break

    # print(r.text)

    soup = BeautifulSoup(r.content, 'html.parser')
    oppContainer = soup.select('.wyg-inner > *') # > p

    # print(oppContainer)
    # csvfile = open('creativeCapital.csv', 'w', newline='', encoding='utf-8')
    # writer = csv.writer(csvfile, delimiter=',')
    # writer.writerow(['title', 'dueDate', 'location', 'notes', 'link', 'typeOfOpportunity', 'approved', 'keywords'])
    print('setup complete, scraping starting....')
    message = ''
    i = 0
    while i < 80:#len(oppContainer) - 2:
        print(i)
        title = ''
        deadline = ''
        location = ''
        description = ''
        website = ''

        if oppContainer[i].name == 'hr':
            try: # some of the opportunities have everything in one strong tag, others are separated between two strongs 
                # print(oppContainer[i + 1].findChild('strong').text)
                # headingList = oppContainer[i + 1].findChild('strong').text.split('\n')
                strongTags = oppContainer[i + 1].find_all('strong') # sometimes this doesn't get all the strong tags
                headingList = strongTags[0].text.split('\n')
                if len(strongTags) > 1:
                    headingList.append(strongTags[1].text)

            except:
                i += 1
                continue

            title = headingList[0]

            try:
                website = oppContainer[i + 1].findChild('strong').findChild('a').attrs['href']
            except:
                website = oppContainer[i + 1].findChild('a')
                if website:
                    website = website.attrs['href']

            # DESCRIPTION -------------------------------------------------------
            try:
                descriptionList = oppContainer[i + 2].findChildren('span')
                if len(descriptionList) > 1:
                    for tag in descriptionList:
                        description += tag.text
                else:
                    description = oppContainer[i + 2].findChild('span').text
            except: # sometimes description is not in a span tag
                description = oppContainer[i + 2].text
            if description.find('Fee') != -1 or len(description) < 10:
                i += 1
                continue

            

            print(title)
            #DEADLINE -------------------------------------------------------------------------------------------
            if len(headingList) == 2:
                deadline = headingList[1]  
            elif len(headingList) == 3:
                deadline = headingList[2]
            
            try:
                if deadline != '': # deadline is 23:59 on the date provided, new date regex needed depending on site's date format
                    deadlineParse = deadline[10:] + ' 23:59'
                    deadlineParse = datetime.strptime(deadlineParse, '%B %d, %Y %H:%M')
                    deadline = datetime.strftime(deadlineParse, '%Y-%m-%d %H:%M:59Z')
            except: # if deadline is grouped together in one tag with location, so does not match above format
                try:
                    deadlineList = deadline.split('\n')
                    deadline = deadlineList[1]
                    deadline = deadline[10:]
                    deadline = datetime.strptime(deadline, '%B %d, %Y %H:%M')
                    deadline = datetime.strftime(deadline, '%d/%m/%Y %H:%M')
                    location = deadlineList[0]
                except:
                    i += 1
                    continue
            if deadline == '':
                i += 1
                continue

            # CHECK IF TITLE / DEADLINE IS ALREADY IN DATABASE, if True, continue
            if ActiveOpps.objects.filter(title=title, deadline=deadline).exists():
                print(f'title {title} already exists in database')
                i += 1
                continue

            #LOCATION -------------------------------------------------------------------------------------------
            if location == '':
                location = headingList[1] if len(headingList) == 3 else ''

            # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'user', 'content': PROMPT + '###' + title + '. ' + description},
                ]
            )

            message = 'Successfully created all new entries.'

            try:
                completion_text = json.loads(str(response.choices[0])) # returns DICT
                content = completion_text['message']['content']
                print(f'json before json conversion = {content}')
                json_result = json.loads(content)
                location = json_result['location'] if json_result['location'] != 'None' else 'Online'
                print(location)
                oppTypeList = findOppTypeTags(description.lower()) # Uses regular search function
                if json_result['keywords'].find(', ') != -1:
                    keywordsList = json_result['keywords'].split(', ')
                else:
                    keywordsList = json_result['keywords'].split(',')
                print(keywordsList)
                print(oppTypeList)
                
                # CREATE A ACTIVEOPPS Model instance and save it to the database
                newModel = ActiveOpps(title=title, deadline=deadline,
                            location=location, description=description, link=website, 
                            typeOfOpp=oppTypeList, approved=True, keywords=keywordsList)
                newModel.save()
            except:
                print('An entry failed to be added.')
                message = 'At least 1 entry failed to be added.'
                i += 1
                continue

            # currentRow = [title, deadline, location, description, website, typeOfOppString, APPROVED, keywordsString]
            # writer.writerow(currentRow)

        i += 1
    return message
                
    # csvfile.close()