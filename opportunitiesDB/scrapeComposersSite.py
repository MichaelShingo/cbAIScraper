import requests, environ, openai, json
from bs4 import BeautifulSoup
from datetime import datetime
from .models import ActiveOpps
from .helperFunctions import tagToStr, findOppTypeTags

# Issues
        # can it filter out anything that has an application fee?
        # if it's missing certain fields, don't put it on the database at all? URL in particular

def scrape():
    PROMPT = '''In the text below, I will provide a description of an opportunity. Based the description, do these 4 things? 
            1. Give me a comma-separated list of relevant keywords that musicians and artists might search for.
            2. If the description mentions an application fee, write "Fee" for the description. If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description using a minimum of 100 words. Include important requirements and any compensation as applicable.
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, state, country" as applicable. If there is no state, leave it out. If you can't find a definite location, write "None".
            4. Choose ONLY from the following list of words: ['Part-Time Job', 'Full-Time Job', 'scholarship', 'grant', 'workshop', 'residency', 'contest',  'paid internship', 'unpaid internship']. Give me a comma-separated sublist of the given list that is relevant to the description provided.
            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","summary":"summary_text","location":"city, state, country","relevant_words":"word1,word2,word3"}
            '''
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

    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0

    for i in range(int(maxPage)): #loops through all pages except last one (low quality opps)
        # if i == 1: # REMOVE THIS IN FINAL VERSION
        #     break
        pageR = requests.get(PAGE_LINK + str(i))
        soup = BeautifulSoup(pageR.content, 'html.parser')
        opportunityRows = soup.select('.views-row .field-content a')
        oppLinks = [row['href'] for row in opportunityRows]
        # k = 0 # FOR TESTING ONLY
        for oppLink in oppLinks: #loops through all opportunities on each page
            # k += 1 # FOR TESTING ONLY
            # if k == 3: # FOR TESTING ONLY
                # break
            try:
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
                    sameEntryCount += 1
                    print(f'title {title} already exists in database')
                    continue

                # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': PROMPT + '###' + title + '. ' + description},
                    ]
                )
        
                completion_text = json.loads(str(response.choices[0])) # returns DICT
                content = completion_text['message']['content']
                print(f'json before json conversion = {content}')
                json_result = json.loads(content)
                location = json_result['location'] if json_result['location'] != 'None' else 'Online'
                # oppTypeList = (json_result['relevant_words']).split(', ') # GPT does not do well with finding oppTypes
                oppTypeList = findOppTypeTags(description.lower()) # Uses regular search function
                
                if json_result['summary'] == 'Fee':
                    fee += 1
                    continue
                elif json_result['summary'] != 'None':
                    description = json_result['summary']
                    
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
        'website': 'Composers Site',
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'fee': str(fee)
    }
    return message