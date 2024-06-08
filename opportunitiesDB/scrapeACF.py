from bs4 import BeautifulSoup
from datetime import datetime
from .models import ActiveOpps
from .helperFunctions import findOppTypeTags, addComposerKeywords, formatTitle, checkDuplicate, getWithScrapeOps, formatDjangoDateString, checkDescriptionContainsFee
from .aiFunctions import getGPTResponse, getAILocation, getKeywordsList
from . import promptText
from reports.saveReportAndMessage import saveReportGenMessage


def scrape():
    PROMPT = f'''{promptText.PROVIDE_OPP_DETAILS}
            1. {promptText.AI_TITLE}
            2. {promptText.SUMMARIZE}
            3. {promptText.KEYWORDS}
            4. {promptText.LOCATION}''' + '''Format the result as a JSON string like this:
            {"aititle":"title - organization_name","description":"summary of the opportunity","keywords":"keyword1,keyword2,keyword3","location":"city, full_state_name, country"}
            '''
    WEBSITE_NAME = 'ACF'

    PAGE_LINK = 'https://composersforum.org/opportunities/?fwp_paged='
    errorMessage = 'None'

    r = getWithScrapeOps(PAGE_LINK + '1')
    soup = BeautifulSoup(r.content, 'html.parser')

    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0
    stop = False
    i = 0
    acfLinks, feeDeadline, summary = [], [], []

    while not stop:
        i += 1
        if i != 1:
            r = getWithScrapeOps(PAGE_LINK + str(i))
            soup = BeautifulSoup(r.content, 'html.parser')
            invalidPage = soup.select('.no-results')
            if len(invalidPage) > 0:
                stop = True
                break
        mainContent = soup.select('main')[0]

        acfLinks += mainContent.select('.is-tight')
        feeDeadline += mainContent.select('.subheadline')
        summary += mainContent.select('p')

    for j in range(len(acfLinks)):
        try:
            # if fee continue
            feeDeadlineText = feeDeadline[j].text
            feeIndex = feeDeadlineText.find('$')
            print(feeIndex, f' fee = {feeDeadlineText[feeIndex + 1]}')

            if feeDeadlineText[feeIndex + 1] != '0':
                fee += 1
                print('fee')
                continue

            deadlineIndex = feeDeadlineText.find('Deadline')
            postedIndex = feeDeadlineText.find('Posted')
            deadlineString = feeDeadlineText[deadlineIndex +
                                             10: postedIndex - 7]
            deadlineWithMidnight = deadlineString + ' 23:59'
            deadlineDate = datetime.strptime(
                deadlineWithMidnight, '%B %d, %Y %H:%M')
            deadlineDate = formatDjangoDateString(deadlineDate)

            title = acfLinks[j].text
            website = acfLinks[j].find('a').attrs['href']

            if checkDuplicate(title, deadlineDate):
                sameEntryCount += 1
                print('duplicate')
                continue

            # ai portion
            detailPageR = getWithScrapeOps(website)
            detailSoup = BeautifulSoup(detailPageR.content, 'html.parser')
            detailMainElement = detailSoup.find('main')
            sidebar = detailSoup.select('.program-info')
            if len(sidebar) > 0:
                sidebarLinkElements = sidebar[0].select('a')
                for detailLink in sidebarLinkElements:
                    if detailLink.text == 'Website':
                        website = detailLink.attrs['href']
                        break

            innerText = detailMainElement.get_text()

            json_result = getGPTResponse(
                PROMPT + '###' + f'Title {title} | ' + str(innerText))
            location = getAILocation(json_result)
            description = json_result['description']
            if checkDescriptionContainsFee(description):
                fee += 1
                continue
            oppTypeList = findOppTypeTags(innerText)
            titleAI = formatTitle(json_result['aititle'])
            keywordsList = getKeywordsList(json_result)
            keywordsList = addComposerKeywords(keywordsList)

            newModel = ActiveOpps(title=title, deadline=deadlineDate, titleAI=titleAI,
                                  location=location, description=description, link=website, deadlineString=deadlineString,
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
