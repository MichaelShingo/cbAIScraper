from .tagLists import typeOfOpportunity, partTime, fullTime
from . import tagLists
import string

def tagToStr(tag): #recursive function that converts tag and its contents to string, including all nested tags
    if isinstance(tag, str):
        return tag
    else:
        if tag.contents:
            return tagToStr(tag.contents[0])
        else:
            return ''
        
def formatLocation(location:str):
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
        
def findOppTypeTags(descriptionLower):
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