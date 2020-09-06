from .models import CovidWeek
from datetime import timedelta
import logging
log = logging.getLogger('api.graph.infections')

IFR=0.01 #infection fatality rate ((IFR)
INV_IFR=1/IFR #inverse IFR
ONSET_TO_DEATH=3 #weeks

def calc():
	"""calculate infection for all stored places"""
	log.info("Calculating raw infection numbers for each place")
	for place in district_names():
		calc_district(place=place)

def calc_district(place='Birmingham'):
	"""calculate infections based on deaths in 3 weeks"""
	for week in CovidWeek.objects.filter(areaname=place).order_by('week'):
		future_week=CovidWeek.objects.filter(areaname=place,week=week.week+ONSET_TO_DEATH)
		
		try:
			last_total=CovidWeek.objects.get(areaname=place,week=week.week-1).estinfectionscum
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
		_updated=False
		if week.estcasesweekly !=est_infections:
			week.estcasesweekly=est_infections
			_updated=True
		if week.estinfectionscum != new_total:
			week.estinfectionscum = new_total
			_updated=True
		if _updated:
			log.debug(f"Infections in {place} stored : {week.estcasesweekly} Infections calculated:{est_infections} Deaths in 3 weeks: {future_C19deaths}")
			log.debug(f"Cumulative in {place} total stored: {week.estinfectionscum} and new total {new_total}")
			week.save()

def districts():
	q=CovidWeek.objects.values('areacode').distinct()	
	return [d['areacode'] for d in q]

def district_names():
	q=CovidWeek.objects.values('areaname').distinct()
	return [d['areaname'] for d in q]
