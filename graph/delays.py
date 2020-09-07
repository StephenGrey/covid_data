from .models import DailyReport
from django.db.models import Sum,Max
from .ons_week import stored_names
import logging
log = logging.getLogger('api.graph.delays')

def calc():
	_date='2020-08-25'
	nat_totaldelay=0
	nat_totalcases=0
	for areacode,areaname in stored_names.items():
		print(areacode)
		q=DailyReport.objects.filter(areacode=areacode,specimenDate=_date).order_by('publag')
		print(q)
		last_total=0
		delay_total=0
		for i in q:
			lag=i.publag
			cases=i.dailycases
			add_cases=cases-last_total
			delay_total+=add_cases*lag
			last_total=cases
			log.info(f'{areaname} - lag: {lag} cases: {cases} addcases: {add_cases}')
		if last_total:
			average_delay=round(delay_total/last_total,2)
		else:
			average_delay=None
		log.info(f'{areaname} - Av delay: {average_delay}')
		nat_totaldelay+=delay_total
		nat_totalcases+=last_total
	nat_avdelay=round(nat_totaldelay/nat_totalcases,2)
	log.info(f'National: total cases {nat_totalcases}; av delay {nat_avdelay}')
		#,publag=10).aggregate(Sum('dailycases')){'dailycases__sum': None}
