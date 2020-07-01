from django.db import models
from .models import CovidWeek
import datetime
one_week=datetime.timedelta(7)

def calc_new_cases():
	for d in districts():
		for w in CovidWeek.objects.filter(areacode=d):
			lastweek=CovidWeek.objects.filter(areacode=d,date=w.date-one_week)
			if lastweek:
				lasttotal=lastweek[0].totcumcases
			else:
				lasttotal=0
			newcases=w.totcumcases-lasttotal
			#print(f'Date: {w.date} CumCases: {w.totcumcases} NewCases: {newcases}')
			w.weeklycases=newcases
			w.save()
		
	return 
	
def districts():
	q=CovidWeek.objects.values('areacode').distinct()
	
	return [d['areacode'] for d in q]

