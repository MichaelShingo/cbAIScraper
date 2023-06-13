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
        
def findOppTypeTags(descriptionLower):
    #Wix tag formatting - ["tag1","tag2"]
    result = []
    for type in typeOfOpportunity:
        if descriptionLower.find(type) >= 0:
            if type in partTime:
                result.append(tagLists.PART_TIME_JOB)
            elif type in fullTime:
                result.append(tagLists.FULL_TIME_JOB)
            elif type == 'call for scores' or type == 'competition':
                result.append('Contest')
            else:
                result.append(string.capwords(type))
    if len(result) == 0:
        result.append('Other')
        
    return result