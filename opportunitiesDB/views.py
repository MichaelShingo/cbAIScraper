from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ActiveOpps
from datetime import datetime
from .serializers import ActiveOppsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .helperFunctions import formatLocation
from django.contrib.auth.models import AnonymousUser
from . import (scrapeAsianArts, 
               scrapeHyperAllergic, 
               scrapeComposersSite, 
               scrapeCreativeCapital)


class ActiveOppsListCreateAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        if isinstance(request.user, AnonymousUser):
            status_code = status.HTTP_403_FORBIDDEN # 401 must include WWW-Authenticate header with instructions on how to authenticate
            return Response({'content': 'Forbidden'}, status=status_code)
        queryset = ActiveOpps.objects.all()
        serializer = ActiveOppsSerializer(queryset, many=True)
        status_code = status.HTTP_200_OK

        return Response(serializer.data, status=status_code)

    def create(self, request):
        pass

opps_list_create_view = ActiveOppsListCreateAPIView.as_view()

class ActiveOppsListMonthAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        today = datetime.today()
        curMonthNum = datetime.strftime(today, '%m')
        queryset = ActiveOpps.objects.filter(createdAt__month=curMonthNum)
        serializer = ActiveOppsSerializer(queryset, many=True)
        status_code = status.HTTP_200_OK

        return Response(serializer.data, status=status_code)
    
opps_list_month_view = ActiveOppsListMonthAPIView.as_view()


class TestModelCreation(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
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
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        try:
            data = ActiveOpps.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data.delete()
        serializer = ActiveOppsSerializer(data)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
    
delete_view = DeleteAPIView.as_view()


class ComposerScrapeAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        message = scrapeComposersSite.scrape()
        data = {'message': message,
                'status': 'success'}
        
        status_code = status.HTTP_202_ACCEPTED

        return Response(data, status=status_code)

composer_scrape_view = ComposerScrapeAPIView.as_view()

class CreativeCapitalScrapeAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        message = scrapeCreativeCapital.scrape()
        status_code = status.HTTP_202_ACCEPTED
        return Response(message, status=status_code)
    
capital_scrape_view = CreativeCapitalScrapeAPIView.as_view()

class AsianArtsScrapeAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        message = scrapeAsianArts.scrape()
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
asian_arts_scrape_view = AsianArtsScrapeAPIView.as_view()

class HyperAllergicScrapeAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        message = scrapeHyperAllergic.scrape()
        data = {'message': message,
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)
    
hyper_scrape_view = HyperAllergicScrapeAPIView.as_view()

class FormatLocationAPIView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        queryset = ActiveOpps.objects.all()
        for obj in queryset:
            print(obj.location)
            obj.location = formatLocation(obj.location)
            print(obj.location)
            print('________________')
            obj.save()
        data = {'message': 'success',
                'status': 'success'}
        status_code = status.HTTP_202_ACCEPTED
        return Response(data, status=status_code)

format_location_view = FormatLocationAPIView.as_view()