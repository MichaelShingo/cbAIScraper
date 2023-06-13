# Web scraper for Creative Capital, saves data in CSV file formatted for upload to Wix
#World cities list attribution - https://simplemaps.com/data/world-cities

import csv
from datetime import datetime
from bs4 import BeautifulSoup
import requests, environ, openai
from .helperFunctions import findOppTypeTags


# ISSUES

def scrape(prompt):
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


    r = requests.get(
    url='https://proxy.scrapeops.io/v1/',
    params={
        'api_key': API_KEY_SCRAPEOPS,
        'url': 'https://creative-capital.org/2023/05/30/artist-opportunities-june-and-july-2023/', 
    },
    )

    # print(r.text)

    soup = BeautifulSoup(r.content, 'html.parser')
    oppContainer = soup.select('.wyg-inner > *') # > p

    # print(oppContainer)
    # csv file created, use this format for data to match Wix collection
    csvfile = open('creativeCapital.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['title', 'dueDate', 'location', 'notes', 'link', 'typeOfOpportunity', 'approved', 'keywords'])

    i = 0
    while i < len(oppContainer) - 2:
        title = ''
        deadline = ''
        location = ''
        description = ''
        website = ''

        if oppContainer[i].name == 'hr': # THIS IS ONLY RUNNING ONCE?????
            print('name = hr')
            try: # some of the opportunities have everything in one strong tag, others are separated between two strongs 
                # print(oppContainer[i + 1].findChild('strong').text)
                # headingList = oppContainer[i + 1].findChild('strong').text.split('\n')
                strongTags = oppContainer[i + 1].find_all('strong')
                headingList = strongTags[0].text.split('\n')
                if len(strongTags) > 1:
                    headingList.append(strongTags[1].text)

            except:
                break
            try:
                website = oppContainer[i + 1].findChild('strong').findChild('a').attrs['href']
            except:
                website = oppContainer[i + 1].findChild('a')
                if website:
                    website = website.attrs['href']
                print(website)
            description = oppContainer[i + 2].findChild('span').text
            title = headingList[0]

            print(title)

            #DEADLINE -------------------------------------------------------------------------------------------
            # print(headingList)
            if len(headingList) == 2:
                deadline = headingList[1]  
            elif len(headingList) == 3:
                deadline = headingList[2]
            
            if deadline != '': #deadline is 23:59 on the date provided, new date regex needed depending on site's date format
                deadline = deadline[10:] + ' 23:59'
                deadline = datetime.strptime(deadline, '%B %d, %Y %H:%M')
                deadline = datetime.strftime(deadline, '%d/%m/%Y %H:%M')

            #LOCATION -------------------------------------------------------------------------------------------
            location = headingList[1] if len(headingList) == 3 else ''

            if location == '':
                location = findLocation(description) 

            #Tags -------------------------------------------------------------------------------------------
            keywordsString = '['
            typeOfOppString = '['
            descriptionLower = description.lower()
            keywordsString = findKeywordTags(descriptionLower)
            typeOfOppString = findOppTypeTags(descriptionLower)
        
            #put all data into a list, which becomes the row in the csv file
            currentRow = [title, deadline, location, description, website, typeOfOppString, APPROVED, keywordsString]
            writer.writerow(currentRow)

            # print(f'title = {title} | location = {location} | deadline = {deadline} | website = {website} | description = {description}')

        i += 1
                
    csvfile.close()