from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, environ, openai, json, csv
from .helperFunctions import findOppTypeTags
from .models import ActiveOpps
from . import tagLists

def scrape():
    # modified prompt to say 'artists' not 'musicians and artists'
    PROMPT = '''In the text below, I will provide a location and description of an opportunity. Based the text, can you do these 3 things? 
            1. Give me a comma-separated list of relevant keywords that artists might search for.
            2. If the description mentions an application fee or entry fee, replace the description with "Fee". If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description in using a minimum of 100 words and a maximum of 150 words. Include important requirements and any compensation as applicable.
            3. Return the location of the opportunity in the format "city, full_state_name, full_country_name." If there is no state, leave it out. If the location is "Remote" or there is no definite location, return "Online".
            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","summary":"summary_text","location":"city, full_state_name, full_country_name","relevant_words":"word1,word2,word3"}
            '''
    OPP_LINK = 'https://www.aaartsalliance.org'
    NONE = 'None'

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

    #SCRAPING ---------------------------------------------------------
    r = requests.get('https://www.aaartsalliance.org/opportunities')
    soup = BeautifulSoup(r.content, 'html.parser')
    opportunityRows = soup.select('.opportunity a')
    oppLinks = [row['href'] for row in opportunityRows]

    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0

    for oppLink in oppLinks: #loops through all opportunities on each page
        try:
            oppR = requests.get(OPP_LINK + oppLink)
            oppSoup = BeautifulSoup(oppR.content, 'html.parser')
            title = oppSoup.select('.large-title')[0].contents[0] if oppSoup.select('.large-title') else NONE
            oppType = oppSoup.select('.mt-3')[4].select('a')[0].text # a tag text inside .mt-3
        
            oppTypeDict = {
                'Job': tagLists.FULL_TIME_JOB,
                'Internship': tagLists.PAID_INTERNSHIP,
                'Call for Submissions': tagLists.CONTEST,
                'Grant': tagLists.GRANT,
                'Competition': tagLists.CONTEST,
                'Volunteer': tagLists.UNPAID_INTERNSHIP,
                'Audition/Casting Call': tagLists.CONTEST,
                'Residency': tagLists.RESIDENCY
            }

            oppType = oppTypeDict[oppType]
            
            descriptionList = []
            descriptionTags = oppSoup.select('.order-1')[1] if oppSoup.select('.order-1') else '' #selects description box
            for pageElement in descriptionTags.children: #how to made one additional \n on <br>'s??? 
                innerText = pageElement.get_text()
                innerText = innerText.replace('\t', '')
                innerText = innerText.replace('  ', '')
                innerText = innerText.replace('\n', '\n\n')
                if innerText != '\n':
                    descriptionList.append(innerText)
            descriptionList.pop()
            description = ''.join(descriptionList[1:])

            # DEADLINE --------------------------------------------------------------------------
            deadlineList = oppSoup.select('.col-8')[1]#.contents[0] if oppSoup.select('.date-display-single') else NONE
            locationString = deadlineList.select('div')[0].contents[0].text
            deadlinePre = deadlineList.select('div')[1].contents[0]
            postedDate = deadlineList.select('div')[2].contents[0]
            postedDate = datetime.strptime(postedDate, '%b %d, %Y')
            postedDate = datetime.strftime(postedDate + timedelta(days=30), '%b %d, %Y')
            deadline = ''
            deadline = deadlinePre if deadlinePre != 'Rolling' else postedDate

            if not deadline == NONE: #deadline is 23:59 on the date provided, new date regex needed depending on site's date format
                deadline += ' 23:59'
                deadline = datetime.strptime(deadline, '%b %d, %Y %H:%M')
                deadline = datetime.strftime(deadline, '%Y-%m-%d %H:%M:59Z')

            if ActiveOpps.objects.filter(title=title, deadline=deadline).exists():
                sameEntryCount += 1
                print(f'title {title} already exists in database')
                continue

            # WEBSITE -------------------------------------------------------
            secondColumn = oppSoup.select('.order-0')[1].select('a')
            website = secondColumn[len(secondColumn) - 1]['href']
            if website.find('@') != -1: # if link is email address, use the page link
                website = OPP_LINK + oppLink
            
            # LOCATION, KEYWORDS, SUMMARY - send description and title to GPT
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'user', 'content': 'Location: ' + locationString + ' ' + PROMPT + '###' + title + '. ' + description},
                ]
            )
        
            completion_text = json.loads(str(response.choices[0])) # returns DICT
            content = completion_text['message']['content']
            json_result = json.loads(content)
            location = json_result['location'] #if json_result['location'] != 'None' else 'Online'
            if location.endswith(' None'):
                    location = location[:-4]

            if json_result['summary'] == 'Fee':
                fee += 1
                continue
            elif json_result['summary'] != 'None':
                description = json_result['summary']

            if json_result['keywords'].find(', ') != -1:
                keywordsList = json_result['keywords'].split(', ')
            else:
                keywordsList = json_result['keywords'].split(',')
            
            newModel = ActiveOpps(title=title, deadline=deadline,
                        location=location, description=description, link=website, 
                        typeOfOpp=[oppType], approved=True, keywords=keywordsList)
            newModel.save()
            successCount += 1
            print(f'added {title}')
      
        except:
            failCount += 1
            print('An entry failed to be added.')
            continue

    message = {
        'website': 'Asian Arts Alliance',
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'fee': str(fee)
    }
    return message            
