from .models import DailyReport
from django.db.models import Sum,Max
from datetime import timedelta,date
from .ons_week import stored_names
from utils import time_utils
from .phe_fetch import fetchdate, Fetch_PHE

import logging,pandas
log = logging.getLogger('api.graph.delays')


class LagCalc():
	def __init__(self,pubdate,data,start_date=date(2020,8,20)):
		self.pubdate=time_utils.parseISO(pubdate).date() #date when data published
		self.data=data #list of entries
		self.start_date=start_date
		
	def process(self):
		for i in self.data:
			datestring=i['specimenDate']
			new_daily=i['newCasesBySpecimenDate']
			if not new_daily: #ignore dates with no cases
				continue
			specimen_datetime=fetchdate(datestring)
			specimen_date=specimen_datetime.date()
			
			if specimen_date < self.start_date:
				continue
			
			
			row=DailyCases.objects.get(specimenDate=specimen_datetime,areacode=i['areaCode'])
			place=i['areaName']
			
			lag=(self.pubdate-specimen_date).days

			
			try:
				assert row.cases_lag is not ''
				stored_lags_raw=eval(row.cases_lag)
				lags=stored_lags_raw
				#lags={n[0]:n[1] for n in stored_lags_raw}
				maxlag=max(lags.keys())
				daytotal=lags[maxlag]
				
				print(f"Place: {place} SpecimenDate: {specimen_date} lag:{lag} lags:{lags} maxlag:{maxlag} storedtotal:{daytotal} newtotal:{new_daily}")
				
				if new_daily!=daytotal:
					if lags.get(lag):
						print(f'Data already entered for {pubdate}')
					else:
						lags[lag]=new_daily
						new_lags=str(lags)
						row.cases_lag=new_lags
						row.save()
				print('No new Data')
				
			except Exception as e:
				print(e)
				lags={}
				lags[lag]=new_daily
				new_lags=str(lags)
				row.cases_lag=new_lags
				row.save()
			
			
class ImportLags(Fetch_PHE):
	"""take a day's cases and store the published cases against publication date"""
	def __init__(self,filepath):
		self.filepath=filepath
		self.open_file(self.filepath)
		self.pubdate=fetchdate(os.path.basename(filepath)[:10]).date()
		print(f'Processing case data published {self.pubdate}')
	
	def open_file(self,path):
		self.data = pandas.read_csv(path, encoding= "utf-8") 
		
	def ingest_all(self):
		"""pull all daily cases from all PHE areas"""
		for place in self.district_codes():
			self.sequence_ingest(place)

			
	def sequence_ingest(self,areacode):
		"""ingest from a particular areacode"""
		data=self.data[self.data['Area code']==areacode]
		areaname=data['Area name'].unique().item()
		log.info(f'Ingesting cases from {areacode}: {areaname}')
		
		counter=0
		for day in data['Specimen date'].unique():
			date=fetchdate(day)
#			try:
#				row=DailyCases.objects.get(specimenDate=date,areacode=areacode)
#			except DailyCases.DoesNotExist:
#				print(f'No record for {areaname} {date}')
#				continue
			this_day=data[data['Specimen date']==day]
			cases=this_day['Daily lab-confirmed cases'].head(1).item()
			if cases:
				
				lag=(self.pubdate-date.date()).days
				print(f'lag:{lag}, {date}, cases {cases}')
				rows=DailyReport.objects.filter(areacode=areacode,specimenDate=date).order_by('-publag')
				if True:
					if rows:
						lastentry=rows[0]
						if lastentry.dailycases !=cases:
							print(f'mismatch for {lag}, {date}, cases {cases}')
							row, created=DailyReport.objects.get_or_create(areacode=areacode,specimenDate=date,publag=lag,dailycases=cases)
							row.save()
						else:
							pass
					else:
						row=DailyReport(areacode=areacode,specimenDate=date,publag=lag)
						row.dailycases=cases
						row.save()
#				except Exception as e:
#					print(e)
#					print (rows, cases,areacode,date,lag)
			
def ImportJsonLags(ImportLags):

	def open_file(self,path):
		self.data = pandas.read_json(path, encoding= "utf-8") 
		
	def sequence_ingest(self,areacode):
		"""ingest from a particular areacode"""
		data=self.data[self.data['areaCode']==areacode]
		areaname=data['areaName'].unique().item()
		log.info(f'Ingesting cases from {areacode}: {areaname}')
		
		counter=0
		for day in data['specimenDate'].unique():
			date=fetchdate(day)
			this_day=data[data['specimenDate']==day]
			cases=this_day['newCasesBySpecimenDate'].head(1).item()
			if cases:
				
				lag=(self.pubdate-date.date()).days
				print(f'lag:{lag}, {date}, cases {cases}')
				rows=DailyReport.objects.filter(areacode=areacode,specimenDate=date).order_by('-publag')
				if True:
					if rows:
						lastentry=rows[0]
						if lastentry.dailycases !=cases:
							print(f'mismatch for {lag}, {date}, cases {cases}')
							row, created=DailyReport.objects.get_or_create(areacode=areacode,specimenDate=date,publag=lag,dailycases=cases)
							row.save()
						else:
							pass
					else:
						row=DailyReport(areacode=areacode,specimenDate=date,publag=lag)
						row.dailycases=cases
						row.save()
#				except Exception as e:
#					print(e)
#					print (rows, cases,areacode,date,lag)
	

			
def import_csvfiles(dirpath):
	""" import csv files of daily published cases to calculate lags"""
	files=[x for x in os.listdir(dirpath) if '.csv' ==x[-4:]]
	for f in files:
		filepath=os.path.join(dirpath,f)
		print(filepath)
		i=ImportLags(filepath)
		i.ingest_all()
		


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

def new_cases(last_update, codes=stored_names.keys()):
	"""delay on cases reported at last update"""
		
	sd=last_update
	lag=0
	delaytotal=0
	total_reported=0
	while lag<30:
		lag+=1
		total_dailyreported=0	
		for report in DailyReport.objects.filter(specimenDate=sd-timedelta(lag),publag=lag,areacode__in=codes):
			newcases=report.dailycases-previous_total(report)
			total_dailyreported+=newcases
		delaytotal+=(lag*total_dailyreported)
		total_reported+=total_dailyreported
		log.debug(f'lag: {lag}  total: {total_dailyreported}')
	if total_reported:
		av_delay=round(delaytotal/total_reported)
	else:
		av_delay='N/A'
	log.info(f'New cases reported on {sd:%d/%m%/%Y}: {total_reported} Av delay: {av_delay}')


def newcases_by_area(last_update):
	""" new casees and delays by area"""
	for areacode in codes():
		place=stored_names.get(areacode)
		if not place:
			continue
		q=DailyReport.objects.filter(areacode=areacode)
		sd=last_update
		lag=0
		delaytotal=0
		total_reported=0
		while lag<30:
			lag+=1
			total_dailyreported=0	
			for report in q.filter(specimenDate=sd-timedelta(lag),publag=lag):
				newcases=report.dailycases-previous_total(report)
				total_dailyreported+=newcases
			delaytotal+=(lag*total_dailyreported)
			total_reported+=total_dailyreported
			log.debug(f'lag: {lag}  total: {total_dailyreported}')
		if total_reported:
			av_delay=round(delaytotal/total_reported)
		else:
			av_delay='N/A'
		log.info(f'{place}: new cases: {last_update:%d/%m/%Y}: {total_reported} Av delay: {av_delay}')
		

def check_pubcases(codes=stored_names.keys()):
	last_update=date.today()
	n=0
	while n <30:
		new_cases(last_update-timedelta(n),codes=codes)
		n+=1
	


		
def previous_total(report):
	try:
		previous=DailyReport.objects.filter(specimenDate=report.specimenDate,areacode=report.areacode,publag__lt=report.publag).order_by('publag')
		#print([(x.dailycases,x.publag) for x in previous])
		return previous.last().dailycases
	except AttributeError as e:
		#print(e)
		#print(report.__dict__)
		return 0

#all codes 

def codes():
	return [x['areacode'] for x in DailyReport.objects.values('areacode').distinct()]
	

def places():
	places=[]
	for x in codes():
		place=stored_names.get(x)
		if not place:
			log.info(f'Missing code: {x}')
		places.append(place)
	return places