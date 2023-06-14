from django.shortcuts import render
from rest_framework import generics, status
from .models import ActiveOpps
from .serializers import ActiveOppsSerializer
from .helperFunctions import tagToStr
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from . import scrapeAsianArts
from . import scrapeHyperAllergic
from . import scrapeArtworkArchive

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
        message = scrapeComposersSite.scrape()
        data = {'message': message,
                'status': 'success'}
        
        # data = ActiveOppsSerializer(newModel).data

        status_code = status.HTTP_202_ACCEPTED

        return Response(data, status=status_code)

composer_scrape_view = ComposerScrapeAPIView.as_view()

class CreativeCapitalScrapeAPIView(APIView):
    def get(self, request):
        message = scrapeCreativeCapital.scrape()
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
capital_scrape_view = CreativeCapitalScrapeAPIView.as_view()

class AsianArtsScrapeAPIView(APIView):
    def get(self, request):
        message = scrapeAsianArts.scrape()
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
asian_arts_scrape_view = AsianArtsScrapeAPIView.as_view()

class ArtworkAllianceScrapeAPIView(APIView):
    def get(self, request):
        message = scrapeArtworkArchive.scrape()
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
artwork_scrape_view = ArtworkAllianceScrapeAPIView.as_view()

class HyperAllergicScrapeAPIView(APIView):
    def get(self, request):
        message = scrapeHyperAllergic.scrape()
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
hyper_scrape_view = HyperAllergicScrapeAPIView.as_view()














