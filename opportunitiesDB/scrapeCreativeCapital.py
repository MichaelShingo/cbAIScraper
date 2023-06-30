# Web scraper for Creative Capital, saves data in CSV file formatted for upload to Wix
#World cities list attribution - https://simplemaps.com/data/world-cities

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, environ, openai, json
from .helperFunctions import findOppTypeTags, formatLocation
from .models import ActiveOpps
from reports.models import Reports

def scrape():
    PROMPT = '''In the text below, I will provide a description of an opportunity. Based the description, do these 4 things? 
            1. Give me a comma-separated list of relevant keywords that musicians and artists might search for.
            2. If the description mentions an application fee or entry fee, replace the description with "Fee".
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, full_state_name, country" as applicable. If there is no state, leave it out. If you can't find a definite location, write "None".
            4. Using less than 12 words, can you generate a title for this opportunity based on it's description? The title should read like a professional job listing. Include the name of the organization or person who posted the opportunity if possible.

            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","description":"description_text","location":"city, full_state_name, country","title":"title - organization_name"}
            '''

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
    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0
    i = 0
    while i < len(oppContainer) - 2:
        print(i)
        title = ''
        deadline = ''
        location = ''
        description = ''
        website = ''
        deadlineString = ''
        deadlineDate = ''
        errorMessage = 'None'

        
        if oppContainer[i].name == 'hr':
            try: # some of the opportunities have everything in one strong tag, others are separated between two strongs 
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

            print(deadline)
            
            try:
                if deadline != '': # deadline is 23:59 on the date provided, new date regex needed depending on site's date format
                    deadlineParse = deadline[10:] + ' 23:59'
                    deadlineParse = datetime.strptime(deadlineParse, '%B %d, %Y %H:%M')
                    deadlineDate = datetime.strftime(deadlineParse, '%Y-%m-%d %H:%M:59Z')
                    deadlineString = datetime.strftime(deadlineParse, '%B %d, %Y')
                    print('!!!!', deadlineString)
            except: # if deadline is grouped together in one tag with location, so does not match above format
                try:
                    deadlineList = deadline.split('\n')
                    deadline = deadlineList[1]
                    deadline = deadline[10:]
                    print('DEADLINE', deadline)
                    deadline = datetime.strptime(deadline, '%B %d, %Y %H:%M')
                    deadlineDate = datetime.strftime(deadline, '%d/%m/%Y %H:%M')
                    deadlineString = datetime.strftime(deadline, '%B %e, %Y')
                    location = deadlineList[0]
                except:
                    i += 1
                    continue
            if deadlineDate == '':
                i += 1
                continue
            
            if ActiveOpps.objects.filter(title=title, deadline=deadlineDate).exists():
                sameEntryCount += 1
                print(f'title {title} already exists in database')
                i += 1
                continue

            #LOCATION -------------------------------------------------------------------------------------------
            if location == '':
                location = headingList[1] if len(headingList) == 3 else ''

            # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
            try:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': PROMPT + '###' + title + '. ' + description},
                    ]
                )
            except:
                failCount += 1
                i += 1
                continue

            try:
                completion_text = json.loads(str(response.choices[0])) # returns DICT
                content = completion_text['message']['content']
                print(f'json before json conversion = {content}')
                json_result = json.loads(content)
                
                if json_result['description'] == 'Fee':
                    fee += 1
                    continue

                if len(description) < 40:
                    continue

                location = json_result['location'] if json_result['location'] != 'None' else 'Online'
                for l in range(2):
                    location = formatLocation(location)
                print(location)
                titleAI = json_result['title']
                oppTypeList = findOppTypeTags(description.lower()) # Uses regular search function
                if json_result['keywords'].find(', ') != -1:
                    keywordsList = json_result['keywords'].split(', ')
                else:
                    keywordsList = json_result['keywords'].split(',')
                print(titleAI, deadlineString)
                
                # CREATE A ACTIVEOPPS Model instance and save it to the database
                newModel = ActiveOpps(title=title, deadline=deadlineDate, titleAI=titleAI,
                            location=location, description=description, link=website, deadlineString=deadlineString,
                            typeOfOpp=oppTypeList, approved=True, keywords=keywordsList, websiteName='Creative Capital')
                newModel.save()
                successCount += 1
            except Exception as e:
                failCount += 1
                print('An entry failed to be added.', str(e))
                errorMessage = str(e)
                i += 1
                continue
        i += 1
    
    report = Reports(website='Creative Capital', failed=str(failCount),
                     successful=str(successCount), duplicates=str(sameEntryCount),
                     fee=str(fee))
    report.save()
    message = {
        'website': 'Creative Capital',
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'error': errorMessage,
    }
    return message