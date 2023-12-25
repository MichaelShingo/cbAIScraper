import requests
import environ
import openai
import json
from bs4 import BeautifulSoup
from datetime import datetime
from .models import ActiveOpps
from .helperFunctions import tagToStr, findOppTypeTags, formatLocation, formatTitle
from reports.models import Reports


def scrape():
    PROMPT = '''In the text below, I will provide a description of an opportunity. Based the description, do these 5 things? 
            1. Give me a comma-separated list of relevant keywords that musicians and artists might search for.
            2. If the description mentions an application fee or entry fee, write ONLY "Fee" in the description field. Do not write anything other than "Fee" in the description field. If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description using a minimum of 100 words. Include important requirements and any compensation as applicable.
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, full_state_name, country" as applicable. If you can't find a state or country, leave them out. If you can't find a definite location, write "None".
            4. Choose ONLY from the following list of words: ['Part-Time Job', 'Full-Time Job', 'scholarship', 'grant', 'workshop', 'residency', 'contest',  'paid internship', 'unpaid internship']. Give me a comma-separated sublist of the given list that is relevant to the description provided.
            5. Using less than 12 words, can you generate a title for this opportunity based on it's description? The title should read like a professional job listing. Include the name of the organization or person who posted the opportunity if possible.

            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","summary":"summary_text","location":"city, full_state_name, country","relevant_words":"word1,word2,word3","title":"title - organization_name"}
            '''
    OPP_LINK = 'http://live-composers.pantheonsite.io'
    # pages start from 0
    PAGE_LINK = 'http://live-composers.pantheonsite.io/opps/results/taxonomy%3A13?page='
    NONE = 'None'

    # OPENAI SETUP
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('AI_KEY')
    openai.api_key = API_KEY

    title = ''
    deadline = None
    location = ''
    description = ''
    website = ''
    deadlineString = ''
    errorMessage = 'None'

    # SCRAPING ---------------------------------------------------------
    r = requests.get(
        'http://live-composers.pantheonsite.io/opps/results/taxonomy%3A13')
    soup = BeautifulSoup(r.content, 'html.parser')
    opportunityRows = soup.select('.views-row .field-content a')
    oppLinks = [row['href'] for row in opportunityRows]
    maxPage = soup.select('.pager-last a')[0].attrs['href'][-1]

    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0

    for i in range(int(maxPage)):  # loops through all pages except last one (low quality opps)
        # if i == 1: # REMOVE THIS IN FINAL VERSION
        #     break
        pageR = requests.get(PAGE_LINK + str(i))
        soup = BeautifulSoup(pageR.content, 'html.parser')
        opportunityRows = soup.select('.views-row .field-content a')
        oppLinks = [row['href'] for row in opportunityRows]
        # k = 0 # FOR TESTING ONLY
        for oppLink in oppLinks:  # loops through all opportunities on each page
            # k += 1 # FOR TESTING ONLY
            # if k == 3: # FOR TESTING ONLY
            # break
            try:
                oppR = requests.get(OPP_LINK + oppLink)
                oppSoup = BeautifulSoup(oppR.content, 'html.parser')
                title = oppSoup.select('.views-field-title .field-content')[
                    0].contents[0] if oppSoup.select('.views-field-title .field-content') else NONE
                descriptionTags = oppSoup.select('p') if oppSoup.select(
                    'p') else ''  # TODO extra spaces are present here
                descriptionList = []

                for tag in descriptionTags:
                    for element in tag.contents:
                        descriptionList.append(tagToStr(element))

                descriptionList.pop()
                description = '\n\n'.join(descriptionList)
                deadline = oppSoup.select(
                    '.date-display-single')[0].contents[0] if oppSoup.select('.date-display-single') else NONE

                # Dates must be YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format
                if not deadline == NONE:
                    deadline += ' 23:59'
                    deadline = datetime.strptime(deadline, '%d %b %Y %H:%M')
                    deadlineDate = datetime.strftime(
                        deadline, '%Y-%m-%d %H:%M:59Z')
                    deadlineString = datetime.strftime(deadline, '%B %d, %Y')

                website = oppSoup.select('.views-field-field-opp-url-url a')[0].attrs['href'] if oppSoup.select(
                    '.views-field-field-opp-url-url a') else OPP_LINK + oppLink

                print(website)

                # CHECK IF TITLE / DEADLINE IS ALREADY IN DATABASE, if True, continue
                if ActiveOpps.objects.filter(title=title, deadline=deadlineDate).exists():
                    sameEntryCount += 1
                    print(f'title {title} already exists in database')
                    continue

                # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': PROMPT +
                            '###' + title + '. ' + description},
                    ]
                )

                completion_text = json.loads(
                    str(response.choices[0]))  # returns DICT
                content = completion_text['message']['content']
                json_result = json.loads(content)
                location = json_result['location'] if json_result['location'] != 'None' else 'Online'
                for l in range(2):
                    location = formatLocation(location)
                # oppTypeList = (json_result['relevant_words']).split(', ') # GPT does not do well with finding oppTypes
                # Uses regular search function
                oppTypeList = findOppTypeTags(description.lower())

                if json_result['summary'] == 'Fee' or json_result['summary'].endswith('Fee') or json_result['summary'].startswith('Fee'):
                    fee += 1
                    continue
                elif json_result['summary'] != 'None':
                    description = json_result['summary']

                if len(description) < 40:
                    continue

                titleAI = json_result['title']
                titleAI = formatTitle(titleAI)

                if json_result['keywords'].find(', ') != -1:
                    keywordsList = json_result['keywords'].split(', ')
                else:
                    keywordsList = json_result['keywords'].split(',')
                composerKeywords = ['composer', 'composition', 'new music']
                keywordsList.extend(composerKeywords)

                # CREATE A ACTIVEOPPS Model instance and save it to the database
                newModel = ActiveOpps(title=title, deadline=deadlineDate, titleAI=titleAI,
                                      location=location, description=description, link=website, deadlineString=deadlineString,
                                      typeOfOpp=oppTypeList, approved=True, keywords=keywordsList, websiteName='Composers Site')
                newModel.save()
                successCount += 1
                print('Added ' + titleAI)

            except Exception as e:
                failCount += 1
                print('An entry failed to be added.', str(e))
                errorMessage = str(e)
                continue

    report = Reports(website='Composers Site', failed=str(failCount),
                     successful=str(successCount), duplicates=str(sameEntryCount),
                     fee=str(fee))
    report.save()

    message = {
        'website': 'Composers Site',
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'fee': str(fee),
        'error': errorMessage
    }
    return message
