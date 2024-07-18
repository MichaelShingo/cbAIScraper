from .tagLists import typeOfOpportunity, partTime, fullTime
from . import tagLists
import string
from .models import ActiveOpps
from datetime import datetime
import environ
import requests


def tagToStr(tag):  # recursive function that converts tag and its contents to string, including all nested tags
    if isinstance(tag, str):
        return tag
    else:
        if tag.contents:
            return tagToStr(tag.contents[0])
        else:
            return ''


def formatTitle(title: str):
    res = title.replace(' - None', '')
    return res


def formatDjangoDateString(datetimeObj):
    return datetime.strftime(
        datetimeObj, '%Y-%m-%d %H:%M:59Z')


def formatDatabaseDateString(datetimeObj):
    return datetime.strftime(datetimeObj, '%B %d, %Y')


def formatLocation(location: str):
    res = location
    if location == 'None':
        res = 'Online'
    elif location.endswith(', None'):
        res = location[:-6]
    elif location.endswith(', USA'):
        res = location[:-5] + ' United States'
    elif location.endswith(', US'):
        res = location[:-4] + ' United States'
    res = res.replace(' None,', '')
    return res


def findOppTypeTags(description):
    descriptionLower = description.lower()
    result = []
    for type in typeOfOpportunity:
        if descriptionLower.find(type) >= 0:
            if type in partTime:
                result.append(tagLists.PART_TIME_JOB)
            elif type in fullTime:
                result.append(tagLists.FULL_TIME_JOB)
            elif type == 'call for scores' or type == 'competition':
                result.append(tagLists.CONTEST)
            elif type == 'fellowship':
                result.append(tagLists.RESIDENCY)
            else:
                result.append(string.capwords(type))
    if len(result) == 0:
        result.append('Other')

    return result


def checkDuplicate(title, deadlineDate):
    if ActiveOpps.objects.filter(title=title, deadline=deadlineDate).exists():
        print(f'title {title} already exists in database')
        return True


def printChars(output_string):
    for char in output_string:
        if char.isspace():
            print(f"Whitespace character: {repr(char)}")
        elif char == '\n':
            print("Newline character")
        elif char == '\t':
            print("Tab character")
        elif char == '\r':
            print("Carriage return character")
        elif char == '\f':
            print("Form feed character")
        else:
            print(f"Other character: {repr(char)}")


def getWithScrapeOps(link):
    env = environ.Env()
    environ.Env.read_env()
    API_KEY_SCRAPEOPS = env('API_KEY_SCRAPEOPS')
    r = requests.get(
        url='https://proxy.scrapeops.io/v1/',
        params={
            'api_key': API_KEY_SCRAPEOPS,
            'url': link,
        })
    return r


def addComposerKeywords(keywordList):
    composerKeywords = ['composer', 'composition', 'new music']
    keywordList.extend(composerKeywords)
    return keywordList


def checkDescriptionContainsFee(description: str) -> bool:
    descriptionLower = description.lower()
    noFee = ['no fee', 'without fee']
    for term in noFee:
        if term in description:
            return False
    if 'fee' in descriptionLower:
        return True
