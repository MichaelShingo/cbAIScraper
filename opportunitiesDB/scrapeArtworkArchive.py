import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import ActiveOpps
from .helperFunctions import findOppTypeTags, formatTitle, checkDuplicate
from .aiFunctions import getGPTResponse, getAILocation, getKeywordsList
from . import promptText
from reports.saveReportAndMessage import saveReportGenMessage


def scrape():
    PROMPT = f'''{promptText.PROVIDE_HTML}
            1. {promptText.AI_TITLE}
            2. {promptText.DESCRIPTION_FREE}
            3. {promptText.KEYWORDS}
            4. {promptText.LOCATION}''' + '''Format the result as a JSON string like this:
            {"aititle":"title - organization_name","description":"description of the opportunity","deadline":"MM/DD/YYYY","keywords":"keyword1,keyword2,keyword3","location":"city, full_state_name, country"}
            '''
    WEBSITE_NAME = 'Artwork Archive'

    currentYear = datetime.now().year
    PAGE_LINK = f'https://www.artworkarchive.com/call-for-entry/complete-guide-to-{currentYear}-artist-grants-opportunities?fee_filter=free&opportunity_search=&opportunity_type_filter%5B%5D=&page='
    errorMessage = 'None'

    # SCRAPING ---------------------------------------------------------
    r = requests.get(PAGE_LINK)
    soup = BeautifulSoup(r.content, 'html.parser')
    paginationList = soup.select('.pagination li ')
    lastListEl = paginationList[len(paginationList) - 2]
    maxPage = int(lastListEl.select_one('a').text)

    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0

    for i in range(1, maxPage + 1):
        print(f'current page = {i}')
        pageR = requests.get(PAGE_LINK + str(i))
        soup = BeautifulSoup(pageR.content, 'html.parser')
        oppRows = soup.select('.opportunity-guide-entry')
        for oppRow in oppRows:
            try:
                # custom scraping
                title = oppRow.select_one('h2').text.split('\n')[1].strip()
                listElements = oppRow.select('li')
                deadlineString = f'December 31, {currentYear}'
                for listElement in listElements:
                    if 'Submission Deadline' in listElement.text:
                        deadlineContent = listElement.text[21:]
                        if deadlineContent == 'Ongoing':
                            deadlineString = deadlineContent
                deadlineString = deadlineString.strip('\n')
                deadlineString += ' 23:59'

                date_object = datetime.strptime(
                    deadlineString, '%B %d, %Y %H:%M')

                # Dates must be YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format
                deadlineDate = datetime.strftime(
                    date_object, '%Y-%m-%d %H:%M:59Z')

                if checkDuplicate(title, deadlineDate):
                    sameEntryCount += 1
                    continue

                linkList = oppRow.select('.external-opportunity-links a')
                for link in linkList:
                    if link.text == 'Learn More':
                        website = link.attrs['href']

                # ai portion
                json_result = getGPTResponse(PROMPT + '###' + str(oppRow))
                location = getAILocation(json_result)
                description = json_result['description']
                oppTypeList = findOppTypeTags(description)
                titleAI = formatTitle(json_result['aititle'])
                keywordsList = getKeywordsList(json_result)
                newModel = ActiveOpps(title=title, deadline=deadlineDate, titleAI=titleAI,
                                      location=location, description=description, link=website, deadlineString=deadlineString[
                                          :-6],
                                      typeOfOpp=oppTypeList, approved=True, keywords=keywordsList, websiteName=WEBSITE_NAME)
                newModel.save()
                successCount += 1
                print('Added ' + titleAI)

            except Exception as e:
                failCount += 1
                print('An entry failed to be added.', str(e))
                errorMessage = str(e)
                continue

    message = saveReportGenMessage(
        WEBSITE_NAME, failCount, successCount, sameEntryCount, fee, errorMessage)

    return message
