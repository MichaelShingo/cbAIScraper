from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, environ, openai, json
from .helperFunctions import findOppTypeTags, formatLocation, formatTitle
from .models import ActiveOpps
from reports.models import Reports

def scrape():
    PROMPT = '''In the text below, I will provide HTML containing information about an opportunity. Based the HTML, can you do these 6 things? 
            1. Extract the description. If the description mentions an application fee or entry fee, replace the description with "Fee".
            2. Extract the deadline date in the format MM/DD/YYYY. If there is no deadline listed, set the date to the last day of the current month.
            3. Extract the title of the opportunity and save it in the "original_title" field.
            3. Extract the hyperlink linking to additional information.
            4. Based on the description, give me a comma-separated list of relevant keywords that artists might search for.
            5. Using less than 12 words, can you generate a title for this opportunity based on it's description and save it in the "aititle" field? The title should read like a professional job listing. Include the name of the organization or person who posted the opportunity if possible.
            6. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, full_state_name, country". If there is no state, leave it out. If you can't find a definite location, write "None". If the location contains a US state, write "United States" for country.
            Format the result as a JSON string like this:
            {"original_title":"title","aititle":"title - organization_name","description":"description of the opportunity","deadline":"MM/DD/YYYY","hyperlink":"url_to_website","keywords":"keyword1,keyword2,keyword3","location":"city, full_state_name, country"}
            '''


    # OPEN AI SETUP
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    API_KEY_SCRAPEOPS = env('API_KEY_SCRAPEOPS')
    openai.api_key = API_KEY


    # GET CURRENT MONTH URL
    try:
      #SCRAPING ---------------------------------------------------------
        today = datetime.today()
        curMonthStr = datetime.strftime(today, '%B')
        prevMonthNum = datetime.strftime(today - timedelta(days=15), '%m')
        nextMonthStr = datetime.strftime(today + timedelta(days=32), '%B')
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
                print(f'WORKING URL = {urlVersion}')
                break

        print('made it')

        
        
        
    except Exception as e:
        message = {
            'website': 'Creative Capital',
            'failed': str(failCount),
            'successful': str(successCount),
            'duplicates': str(sameEntryCount),
            'fee': str(fee),
            'error': 'Failed to find valid URL - ' + str(e)
        }
        return message
    
    soup = BeautifulSoup(r.content, 'html.parser')
    oppContainer = soup.select('.wyg-inner > *') # > p
    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0
    errorMessage = 'None'
    for i in range(len(oppContainer) - 2):
        try:
            print(i)
            title = ''
            deadline = ''
            location = ''
            description = ''
            website = ''
            deadlineString = ''
            deadlineDate = ''
            

            print(oppContainer[i].name)

            aiInput = None
            if oppContainer[i].name == 'hr': # take the next 1 or 2 p tags,
                print('WE HAVE AN HR')
                if oppContainer[i + 2] == 'hr':
                    aiInput = str(oppContainer[i + 1])
                else:
                    aiInput = str(oppContainer[i + 1]) + str(oppContainer[i + 2])


                # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': PROMPT + '###' + aiInput},
                    ]
                )

                completion_text = json.loads(str(response.choices[0])) # returns DICT
                content = completion_text['message']['content']
                json_result = json.loads(content)
                location = json_result['location'] if json_result['location'] != 'None' else 'Online'

                description = json_result['description']

                if description == 'Fee':
                    fee += 1
                    continue
                elif len(description) < 40:
                    continue

                oppTypeList = findOppTypeTags(description.lower()) # Uses regular search function
                location = json_result['location']
                for l in range(2):
                    location = formatLocation(location)

                deadline = json_result['deadline']
                if deadline != 'None':
                    deadline += ' 23:59'
                    deadline = datetime.strptime(deadline, '%m/%d/%Y %H:%M')
                else:
                    deadline = datetime.strftime(datetime.today() + timedelta(days=30))
                
                deadlineDate = datetime.strftime(deadline, '%Y-%m-%d %H:%M:59Z')
                deadlineString = datetime.strftime(deadline, '%B %d, %Y')

                title = json_result['original_title']
                titleAI = json_result['aititle']
                titleAI = formatTitle(titleAI)

                if title == 'None':
                    continue
                
                website = json_result['hyperlink']

                if ActiveOpps.objects.filter(title=title, deadline=deadlineDate).exists():
                    sameEntryCount += 1
                    print(f'title {title} already exists in database')
                    continue

                if json_result['keywords'].find(', ') != -1:
                    keywordsList = json_result['keywords'].split(', ')
                else:
                    keywordsList = json_result['keywords'].split(',')
                composerKeywords = ['composer', 'composition', 'new music']
                keywordsList.extend(composerKeywords)
                print(title, )
                # CREATE A ACTIVEOPPS Model instance and save it to the database
                newModel = ActiveOpps(title=title, deadline=deadlineDate, titleAI=titleAI,
                            location=location, description=description, link=website, deadlineString=deadlineString,
                            typeOfOpp=oppTypeList, approved=True, keywords=keywordsList, websiteName='Creative Capital')
                newModel.save()
                successCount += 1
                print(f'Added | {title}')
            

        
        except Exception as e:
            failCount += 1
            print(str(e))
            continue

    
    report = Reports(website='Creative Capital', failed=str(failCount),
                        successful=str(successCount), duplicates=str(sameEntryCount),
                        fee=str(fee))
    report.save()
    message = {
        'website': 'Creative Capital',
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'fee': str(fee),
        'error': errorMessage
    }
    return message


    

    
