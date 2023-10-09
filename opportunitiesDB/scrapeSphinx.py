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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def scrape():
    # driver = webdriver.Chrome()
    url = 'https://www.sphinxmusic.org/job-postings'
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
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

    return 'hi'
