from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
import requests
import environ
import json
from .helperFunctions import findOppTypeTags, formatLocation, formatTitle, checkDuplicate, formatDatabaseDateString, formatDjangoDateString, checkDescriptionContainsFee
from .models import ActiveOpps
from reports.models import Reports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from . import gptFunctions
from selenium.webdriver.support.ui import WebDriverWait
import time
from .sphinxTestData import tempData
from .aiFunctions import getGPTResponse, getAILocation, getKeywordsList
from . import promptText
from reports.saveReportAndMessage import saveReportGenMessage

# web driver MUST be exited after each use, even if it's an error


def scrape():
    PROMPT = f'''{promptText.PROVIDE_ALL_TEXT}
            1. {promptText.AI_TITLE}
            2. {promptText.DESCRIPTION_FREE} If the text does not contain information about an opportunity, write "none" in the description field.
            3. {promptText.KEYWORDS}
            4. {promptText.LOCATION}''' + '''Format the result as a JSON string like this:
            {"aititle":"title - organization_name","description":"description of the opportunity","deadline":"MM/DD/YYYY","keywords":"keyword1,keyword2,keyword3","location":"city, full_state_name, country"}
            '''
    WEBSITE_NAME = 'Sphinx'
    failCount, successCount, sameEntryCount, fee = 0, 0, 0, 0
    errorMessage = 'None'

    print('browserless!')  # should you abstract this out and return the driver?
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('API_KEY_BROWSERLESS')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability('browserless:token', API_KEY)
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")

    url = 'https://www.sphinxmusic.org/job-postings'
    driver = webdriver.Remote(
        command_executor='https://chrome.browserless.io/webdriver',
        options=chrome_options
    )

    driver.get(url)
    time.sleep(10)
    data = []
    try:

        pagination_links = driver.find_elements(
            By.CLASS_NAME, 'pagination-item')

        maxPage = 1
        if len(pagination_links) > 0:
            maxPage = int(pagination_links[-2].text)

        print('getting page elements, maxpage=', maxPage)
        for i in range(maxPage):
            print(i)
            title_elements = driver.find_elements(
                By.CLASS_NAME, 'table-cell-1')
            deadline_elements = driver.find_elements(
                By.CLASS_NAME, 'table-cell-4')
            link_elements = driver.find_elements(By.CLASS_NAME, 'table-cell-2')

            for j in range(len(title_elements)):
                data.append({'organization': title_elements[j].text, 'deadline': deadline_elements[j].text,
                            'link': link_elements[j].find_element(By.CSS_SELECTOR, 'a').get_attribute('href'),
                             'title': link_elements[j].text})

            if i < maxPage - 1:
                pagination_links = driver.find_elements(
                    By.CLASS_NAME, 'pagination-item')
                next_page_button = pagination_links[-1].find_element(
                    By.CSS_SELECTOR, 'a')
                print(next_page_button)
                next_page_button.click()
                print('clicked')
                time.sleep(10)
    except Exception as e:
        print('Exception:', e)
        driver.quit()

    driver.quit()

    for opp in data:
        try:
            # r = driver.get(opp['link'])
            # html = driver.page_source  # HTML string
            website = opp['link']
            r = requests.get(website)  # replace with selenium?
            soup = BeautifulSoup(r.content, 'html.parser')
            text = soup.get_text(separator=' ')
            title = opp['title']
            deadlineDateObj = datetime.strptime(
                opp['deadline'] + ' 23:59', '%m/%d/%y %H:%M')
            deadline = formatDjangoDateString(deadlineDateObj)
            deadlineString = formatDatabaseDateString(deadlineDateObj)

            if deadlineDateObj.date() < date.today():
                print('deadline has passed')
                continue

            if checkDuplicate(title, deadline):
                sameEntryCount += 1
                continue

            json_result = getGPTResponse(
                f'{PROMPT} ### Title and Organization: {title} - {opp["organization"]} ### {text[:4000]}')
            description = json_result['description']

            if checkDescriptionContainsFee(description):
                fee += 1
                continue

            if description.lower() == 'none':
                print(title, 'There is a problem with the page.')
                failCount += 1
                continue
            oppTypeList = findOppTypeTags(description)
            location = getAILocation(json_result)
            oppTypeList = findOppTypeTags(description)
            titleAI = formatTitle(json_result['aititle'])
            keywordsList = getKeywordsList(json_result)

            newModel = ActiveOpps(title=title, deadline=deadline, titleAI=titleAI,
                                  location=location, description=description, link=website, deadlineString=deadlineString,
                                  typeOfOpp=oppTypeList, approved=True, keywords=keywordsList, websiteName=WEBSITE_NAME)
            newModel.save()
            successCount += 1
            print('Added ' + titleAI)
        except Exception as e:
            failCount += 1
            print('An entry failed to be added.', str(e))
            errorMessage += f'| {str(e)}'
            continue

    message = saveReportGenMessage(
        WEBSITE_NAME, failCount, successCount, sameEntryCount, fee, errorMessage)

    return message
