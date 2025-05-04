# cbAIScraper

A Django Rest Framework API that integrates with OpenAI to help completely automate web scraping and populating Creative Baggage's opportunities database.

## Setup 
1. Install the python version specified in runtime.txt (3.11.3).
2. In the project directly, run ```py -m venv env``` to create a virtual environment.
3. ```env/scripts/activate``` to activate.
4. ```pip install -r requirements.txt```
5. If Microsoft Visual C++ 14.0 required error, https://www.scivision.dev/python-windows-visual-c-14-required/
6. Setup environment variables in .env file in /backend folder.
6. If not migrated: ```py manage.py migrate```
7. If no superuser: ```py manage.py createsuperuser```
8. ```py manage.py runserver```
9. API routes are in the following format: http://localhost:8000/api/opportunities/scrapeComposer with endpoints found in opportunitiesDB/urls.py