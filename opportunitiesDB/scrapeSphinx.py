from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import environ
import openai
import json
from .helperFunctions import findOppTypeTags, formatLocation, formatTitle
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


def download_selenium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)


def scrape():
    print('browserless!')
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('API_KEY_BROWSERLESS')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability('browserless:token', API_KEY)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    try:
        driver = webdriver.Remote(
            command_executor='https://chrome.browserless.io/webdriver',
            options=chrome_options
        )

        driver.get("https://www.example.com")
        print(driver.title)
        driver.quit()
    except Exception as e:
        print('exception')
        return e

    return 'succeeded'


def scrapeOld():

    # driver = webdriver.Chrome()
    url = 'https://www.sphinxmusic.org/job-postings'
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options, service=ChromeService(
        ChromeDriverManager().install()))
    # driver = webdriver.Chrome(service=Service(
    #     ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    # title_elements = driver.find_elements(By.CLASS_NAME, 'table-cell-1')/
    link_elements = driver.find_elements(By.CLASS_NAME, 'table-cell-2')
    # deadline_elements = driver.find_elements(By.CLASS_NAME, 'table-cell-4')
    # pagination_elements = driver.find_elements(
    #     By.CLASS_NAME, 'pagination-item')

    # for element in title_elements:
    #     print(element.text)

    # for element in deadline_elements:
    #     print(element.text)

    for element in link_elements:
        link_element = element.find_element(By.TAG_NAME, 'a')
        print(link_element.get_attribute('href'))

    driver.quit()
    return 'hi'
