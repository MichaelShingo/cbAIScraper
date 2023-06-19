from rest_framework.generics import ListAPIView
from .models import Reports
from .serializers import ReportsSerializer
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rest_framework.response import Response
import environ, pprint, ssl
from email.message import EmailMessage

class ReportsListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Reports.objects.all()
    serializer_class = ReportsSerializer

reports_list_view = ReportsListView.as_view()


class ReportsTodayView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    today = datetime.today()
    curMonthNum = datetime.strftime(today, '%m')
    queryset = Reports.objects.filter(createdAt__month=curMonthNum)
    serializer_class = ReportsSerializer

reports_today_view = ReportsTodayView.as_view()


class ReportsEmailView(APIView):
    def get(self, request):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]
        env = environ.Env()
        environ.Env.read_env()
        sender_email = env('SENDER_EMAIL')
        recipientList = [env('RECIPIENT1'), env('RECIPIENT2')]
        sender_password = env('SENDER_PASSWORD')

        today = datetime.today()
        curMonth = datetime.strftime(today, '%B')
        curMonthNum = datetime.strftime(today, '%m')
        curYear = datetime.strftime(today, '%Y')
        subject = f'Opportunity Scraping Report {curMonth} {curYear}'
        queryset = Reports.objects.filter(createdAt__month=curMonthNum)
        serializer = ReportsSerializer(queryset, many=True)
        data = serializer.data
        body = ''
        for report in data:
            body += f'Website: {report["website"]}\n'
            body += f'Failed: {report["failed"]}\n'
            body += f'Successful: {report["successful"]}\n'
            body += f'Duplicates: {report["duplicates"]}\n'
            body += f'Fee: {report["fee"]}\n\n'

        message = EmailMessage()
        message['From'] = sender_email
        message['To'] = ', '.join(recipientList)
        message['Subject'] = subject
        message.set_content(body)
        
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender_email, sender_password)
            for recipient in recipientList:
                smtp.sendmail(sender_email, recipient, message.as_string())

        status_code = status.HTTP_200_OK

        return Response(data, status=status_code)
    
reports_email_view = ReportsEmailView.as_view()

