from reports.models import Reports


def saveReportGenMessage(websiteName, failCount, successCount, sameEntryCount, fee, errorMessage):
    report = Reports(website=websiteName, failed=str(failCount),
                     successful=str(successCount), duplicates=str(sameEntryCount),
                     fee=str(fee))
    report.save()

    message = {
        'website': websiteName,
        'failed': str(failCount),
        'successful': str(successCount),
        'duplicates': str(sameEntryCount),
        'fee': str(fee),
        'error': errorMessage
    }

    return message
