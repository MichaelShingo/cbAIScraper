#! Web scraper for Composers Site, saves data in CSV file formatted for upload to Wix
#World cities list attribution - https://simplemaps.com/data/world-cities
#TODO put some sections inside functions


##### NAMMMMMMMMMMMMMMMMMMMMMMMMMMMM

import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests, environ, openai, json
from .helperFunctions import findOppTypeTags
from .models import ActiveOpps

def scrape():
    # motified prompt to say 'artists' not 'musicians and artists'
    PROMPT = '''In the text below, I will provide a description of an opportunity. Based the description, do these 3 things? 
            1. Give me a comma-separated list of relevant keywords that artists might search for.
            2. If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description using a minimum of 100 words. Include important requirements and any compensation as applicable.
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, full state name, country" as applicable. If there is no state, leave it out. If you can't find a definite location, write "None".
            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","summary":"summary_text","location":"city, state, country","relevant_words":"word1,word2,word3"}
            '''
    OPP_LINK = 'https://www.artworkarchive.com/'
    PAGE_LINK = 'https://www.artworkarchive.com/call-for-entry/complete-guide-to-2023-artist-grants-opportunities' #pages start from 0
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
    openai.api_key = API_KEY

    #SCRAPING ---------------------------------------------------------
    r = requests.get('https://www.artworkarchive.com/call-for-entry/complete-guide-to-2023-artist-grants-opportunities')
    soup = BeautifulSoup(r.content, 'html.parser')
    opportunityRows = soup.select('.views-row .field-content a')
    oppLinks = [row['href'] for row in opportunityRows]
    maxPage = soup.select('.pager-last a')[0].attrs['href'][-1]

    #csv file created, use this format for data to match Wix collection
    csvfile = open('artworkarchive.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['title', 'dueDate', 'location', 'notes', 'link', 'typeOfOpportunity', 'approved', 'keywords'])

    for i in range(int(maxPage) + 1): #loops through all pages
        pageR = requests.get(PAGE_LINK + str(i))
        soup = BeautifulSoup(pageR.content, 'html.parser')
        opportunityRows = soup.select('.views-row .field-content a')
        oppLinks = [row['href'] for row in opportunityRows]

        for oppLink in oppLinks: #loops through all opportunities on each page
            keywordsString = '['
            typeOfOppString = '['
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
            if not deadline == NONE: #deadline is 23:59 on the date provided, new date regex needed depending on site's date format
                deadline += ' 23:59'
                deadline = datetime.strptime(deadline, '%d %b %Y %H:%M')
                deadline = datetime.strftime(deadline, '%d/%m/%Y %H:%M')

            if ActiveOpps.objects.filter(title=title, deadline=deadline).exists():
                print(f'title {title} already exists in database')
                i += 1
                continue

            website = oppSoup.select('.views-field-field-opp-url-url a')[0].contents[0] if oppSoup.select('.views-field-field-opp-url-url a') else ''
            
            #LOCATION -------------------------------------------------------------------------------------------
            #TODO improve the location function, prioritize finding US states? except Georgia
            # location = findLocation(description) 
            
            #Tags -------------------------------------------------------------------------------------------
            descriptionLower = description.lower()
            # keywordsString = findKeywordTags(descriptionLower)
            typeOfOppString = findOppTypeTags(descriptionLower)
            
            #put all data into a list, which becomes the row in the csv file
            currentRow = [title, deadline, location, description, website, typeOfOppString, APPROVED, keywordsString]
            writer.writerow(currentRow)
                
    csvfile.close()