from django.shortcuts import render
from rest_framework import generics, status
from .models import ActiveOpps
from .serializers import ActiveOppsSerializer
from .helperFunctions import tagToStr
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from . import scrapeComposersSite, scrapeCreativeCapital


class ActiveOppsListCreateAPIView(generics.ListCreateAPIView):
    queryset = ActiveOpps.objects.all()
    serializer_class = ActiveOppsSerializer

opps_list_create_view = ActiveOppsListCreateAPIView.as_view()


class TestModelCreation(APIView):
    def get(self, request):
        newModel = ActiveOpps(title='override get method 2', deadline='2020-10-08 09:33:37-0700',
                            location='Utrecht', description='Ik spreek engels en jij spreekt Nederlands', link='ind.nl', 
                            typeOfOpp=['full time job'], approved=False, keywords=['test', 'application'])
        newModel.save()
        data = {'message': 'Successfully created new entry.',
                'status': 'success'}
        data = ActiveOppsSerializer(newModel).data
        status_code = status.HTTP_202_ACCEPTED

        return Response(data, status=status_code)


test_model_creation = TestModelCreation.as_view()

PROMPT = '''In the text below, I will provide a description of an opportunity. Based the description, do these 4 things? 
            1. Give me a comma-separated list of relevant keywords that musicians and artists might search for.
            2. If the description is less than 150 words, return "None". If the description is greater than 150 words, summarize the description using a minimum of 100 words. Include important requirements and any compensation as applicable.
            3. Give me the location of the opportunity based on any words that suggest a place. If there is no location listed, try to find the location of the university, college, or organization in the description. Location should be in the format "city, state, country" as applicable. If there is no state, leave it out. If you can't find a definite location, write "None".
            4. Choose ONLY from the following list of words: ['Part-Time Job', 'Full-Time Job', 'scholarship', 'grant', 'workshop', 'residency', 'contest',  'paid internship', 'unpaid internship']. Give me a comma-separated sublist of the given list that is relevant to the description provided.
            Format the result as a JSON string like this:
            {"keywords":"keyword1,keyword2,keyword3","summary":"summary_text","location":"city, state, country","relevant_words":"word1,word2,word3"}
            '''

class DeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            data = ActiveOpps.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
delete_view = DeleteAPIView.as_view()


class ComposerScrapeAPIView(APIView):
    def get(self, request):
        message = scrapeComposersSite.scrape(PROMPT)
        data = {'message': message,
                'status': 'success'}
        
        # data = ActiveOppsSerializer(newModel).data

        status_code = status.HTTP_202_ACCEPTED

        return Response(data, status=status_code)

composer_scrape_view = ComposerScrapeAPIView.as_view()

class CreativeCapitalScrapeAPIView(APIView):
    def get(self, request):
        message = scrapeCreativeCapital.scrape(PROMPT)
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
capital_scrape_view = CreativeCapitalScrapeAPIView.as_view()














