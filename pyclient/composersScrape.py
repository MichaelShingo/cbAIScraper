# Web scraper for Composers Site, saves data in CSV file formatted for upload to Wix
#World cities list attribution - https://simplemaps.com/data/world-cities

# can this script be triggered when you call an api endpoint? Fetch can run from Wix every month to this endpoint, triggering the scraping.
# Then 1 hour later, fetch runs to get the data and put it into Wix
# Run the scrape, save data as a list of dictionaries (json)
# Loop through the list, send title, description to GPT, ask it to do the following:



from datetime import datetime
from bs4 import BeautifulSoup
import requests


def tagToStr(tag): #recursive function that converts tag and its contents to string, including all nested tags
    if isinstance(tag, str):
        return tag
    else:
        if tag.contents:
            return tagToStr(tag.contents[0])
        else:
            return ''
        
OPP_LINK = 'http://live-composers.pantheonsite.io'
PAGE_LINK = 'http://live-composers.pantheonsite.io/opps/results/taxonomy%3A13?page=' #pages start from 0
NONE = 'None'
APPROVED = 'FALSE'

PROMPT = '''In the following messages, I will provide a series of descriptions of opportunities. Based the description, can you do these 4 things? 
    1. Give me a list of relevant keywords that musicians and artists might search for.
    2. If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description in 150 words or less, being sure to include important requirements and any compensation as applicable. Else the description should be an empty string.
    3. Give me the location of the opportunity. Location should be in the format "city, state, country" as applicable.
    4. Choose ONLY from the following list of words: ['part-time', 'full-time', 'scholarship', 'grant', 'workshop', 'residency', 'contest',  'paid internship', 'unpaid internship']. Give me a sublist of the given list that is relevant to the description provided.
    Format all 4 results in JSON and return it to me.'''

title = ''
deadline = '' #if none provided, use NONE
location = '' #if none found, use ONLINE
description = ''
website = ''

#SCRAPING ---------------------------------------------------------
r = requests.get('http://live-composers.pantheonsite.io/opps/results/taxonomy%3A13')
soup = BeautifulSoup(r.content, 'html.parser')
opportunityRows = soup.select('.views-row .field-content a')
oppLinks = [row['href'] for row in opportunityRows]
maxPage = soup.select('.pager-last a')[0].attrs['href'][-1]

json = {}

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

        website = oppSoup.select('.views-field-field-opp-url-url a')[0].contents[0] if oppSoup.select('.views-field-field-opp-url-url a') else ''
        
        # CHECK IF TITLE / DEADLINE IS ALREADY IN DATABASE, if True, continue

        # LOCATION, KEYWORDS, OPPTYPE - send description and title to GPT
        
        # CREATE A ACTIVEOPPS Model instance and save it to the database
        currentRow = [title, deadline, location, description, website, typeOfOppString, APPROVED, keywordsString]
            
