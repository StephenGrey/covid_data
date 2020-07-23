from .models import CovidWeek
from datetime import timedelta

IFR=0.01 #infection fatality rate ((IFR)
INV_IFR=1/IFR #inverse IFR
ONSET_TO_DEATH=21 #days

def calc():
	"""calculate infection for all stored places"""
	for place in district_names():
		calc_district(place=place)

def calc_district(place='Birmingham'):
	"""calculate infections based on deaths in 3 weeks"""
	for week in CovidWeek.objects.filter(areaname=place).order_by('date'):
		future_week=CovidWeek.objects.filter(areaname=place,date=week.date+timedelta(ONSET_TO_DEATH))
		
		try:
			last_total=CovidWeek.objects.get(areaname=place,date=week.date-timedelta(7)).estinfectionscum
			if last_total is None:
				last_total=0
		except:
			last_total=0
			
		future_C19deaths=None
		est_infections=None
		new_total=None		
		if future_week:
			future_C19deaths=future_week[0].weeklydeaths
			if future_C19deaths is not None:
				"""MAIN CALCULATION"""
				est_infections=future_C19deaths*INV_IFR
				new_total=est_infections+last_total
		print(f"Infections stored: {week.estcasesweekly} Infections calculated:{est_infections} Deaths in 3 weeks: {future_C19deaths}")
		print(f"Cumulative total stored: {week.estinfectionscum} and new total {new_total}")
		_updated=False
		if week.estcasesweekly !=est_infections:
			week.estcasesweekly=est_infections
			_updated=True
			print('Infections updated')
		if week.estinfectionscum != new_total:
			week.estinfectionscum = new_total
			_updated=True
			print('Total updated')
		week.save() if _updated else None

def districts():
	q=CovidWeek.objects.values('areacode').distinct()	
	return [d['areacode'] for d in q]

def district_names():
	q=CovidWeek.objects.values('areaname').distinct()
	return [d['areaname'] for d in q]
