PROVIDE_HTML = 'In the text below, I will provide HTML containing information about an opportunity. Based the HTML, can you do the following?'

DESCRIPTION = 'Extract the description. If the description mentions an application fee or entry fee, write ONLY "Fee" in the description field. Do not write anything other than "Fee" in the description field.'

DEADLINE = 'Extract the deadline date in the format MM/DD/YYYY. If there is no deadline listed, set the date to the last day of the current month.'

TITLE = 'Extract the title of the opportunity and save it in the "original_title" field.'

HYPERLINK = 'Extract the hyperlink linking to additional information.'

KEYWORDS = 'Based on the description, give me a comma-separated list of relevant keywords that artists might search for.'

AI_TITLE = '''Using less than 12 words, can you generate a title for this opportunity based on it's description and save it in the "aititle" field? The title should read like a professional job listing. Include the name of the organization or person who posted the opportunity if possible.'''

LOCATION = '''6. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, full_state_name, country". If there is no state, leave it out. If you can't find a definite location, write "None". If the location contains a US state, write "United States" for country.'''

RESULT = '{"original_title":"title","aititle":"title - organization_name","description":"description of the opportunity","deadline":"MM/DD/YYYY","hyperlink":"url_to_website","keywords":"keyword1,keyword2,keyword3","location":"city, full_state_name, country"}'

DESCRIPTION_FREE = 'Extract the description of the opportunity. If the description is greater than 150 words, summarize it using a minimum of 100 words and a maximum of 150 words. Include important requirements and any compensation as applicable.'

PROVIDE_ALL_TEXT = 'In the text below, I will provide all of the text contained on a webpage about an artist opportunity. Based on this, can you do the following?'
