from .models import DailyReport, DailyCases
from django.db.models import Sum,Max,Count
from datetime import timedelta,date
from .ons_week import stored_names,english,scottish,nirish,welsh
from utils import time_utils
from .phe_fetch import fetchdate, Fetch_PHE, Check_PHE,Cov19API
from .import_csv import DATA_STORE

import logging,pandas,os,json
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
			
class ImportJsonLags(ImportLags):
	"""ingest published cases from one day """
	def open_file(self,path):
		self.data = pandas.read_json(path, encoding= "utf-8") 
		
	def district_codes(self):
		return sorted([z for z in self.data['areaCode'].unique()])
		
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
			if cases and not pandas.isnull(cases):
				lag=(self.pubdate-date.date()).days
				log.info(f'lag:{lag}, {date}, cases {cases}')
				last_entry=DailyReport.objects.filter(areacode=areacode,specimenDate=date,publag__lt=lag).order_by('publag').last()				
				if last_entry:
					lastcount=last_entry.dailycases 
					if lastcount ==cases:
						continue
					else:
						log.info(f'mismatch for {date} - lag{lag}, cases {cases} (last count was {lastcount})')
				row, created=DailyReport.objects.get_or_create(areacode=areacode,specimenDate=date,publag=lag)
				row.dailycases=cases
				row.save()
	
			
def import_csvfiles(dirpath):
	""" import csv files of daily published cases to calculate lags"""
	files=[x for x in os.listdir(dirpath) if '.csv' ==x[-4:]]
	for f in files:
		filepath=os.path.join(dirpath,f)
		print(filepath)
		i=ImportLags(filepath)
		i.ingest_all()
		
		
def importjsons(dirpath):
	files=[x for x in os.listdir(dirpath) if '.json' ==x[-5:]]
	for f in files:
		filepath=os.path.join(dirpath,f)
		print(filepath)
		i=ImportJsonLags(filepath)
		i.ingest_all()
	
		
def total_publishedcases(path):
	i=ImportLags(filepath)
	
#	data=self.data[self.data['Area code']==areacode]
#		areaname=data['Area name'].unique().item()
#		log.info(f'Ingesting cases from {areacode}: {areaname}')
#



def calc():
	_date='2020-08-25'
	nat_totaldelay=0
	nat_totalcases=0
	lagtotals={} #count cases for each daily delay
	for areacode,areaname in stored_names.items():
		log.debug(areacode)
		q=DailyReport.objects.filter(areacode=areacode,specimenDate=_date).order_by('publag')
		last_total=0
		delay_total=0
		for i in q:
			lag=i.publag
			cases=i.dailycases
			add_cases=cases-last_total
			delay_total+=add_cases*lag
			lagtotals[lag]=lagtotals.get(lag,0)+add_cases
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


def last7():
	"""check delays last 7 days of updates"""
	_date=date.today()
	_end=_date-timedelta(7)
	
	sum_delays={}
	
	#add up all the cases in each area
	while _date > _end:
		day_delays=newcases_by_area(_date)
		
		#update total
		for areacode,v in day_delays.items():
			areatotal=sum_delays.get(areacode,{})
		
			areatotal['delay_total']=areatotal.get('delay_total',0)+v['delay_total']
			areatotal['total_reported']=areatotal.get('total_reported',0)+v['total_reported']
		
			stored_distro=areatotal.get('distribution',{})
			for lag in v['distribution']:
				stored_distro[lag]=stored_distro.get(lag,0)+v['distribution'][lag]
			areatotal['distribution']=stored_distro

			sum_delays[areacode]=areatotal
		
		
		
		_date-=timedelta(1)
		#print(_date)
	
	
	#sum_delays={k:v for k,v in sorted(sum_delays.items(), key=lambda item: item[1].get('av_delay'))}
	all_cases=0
	all_delay=0
	delay_scores={}
	
	#calculate the average for each area
	try:
		for areacode,v in sum_delays.items():
			place=stored_names[areacode]
			delay_total=v['delay_total']
			total_reported=v['total_reported']
			av_delay=round((delay_total/total_reported),2)
			distro=v['distribution']
			log.info(f'{place} : {av_delay} Total:{total_reported} Distrubution:{distro}')
			delay_scores[place]=av_delay
			all_cases+=total_reported
			all_delay+=delay_total
		tot_delay=round((all_delay/all_cases),2)
		log.info(f'Total av delay: {tot_delay}')
	except Exception as e:
		log.error(e)
	
	
	try:
		delay_scores={k:v for k,v in sorted(delay_scores.items(), key=lambda item: item[1])}
		"""save the last 7 days - with pub date"""
		filepath=os.path.join(DATA_STORE,f"{_date:%Y-%m-%d} Last7Delays.json")
		with open(filepath, 'w') as outfile:
			json.dump(delay_scores, outfile)
		"""save the last 7 days - overwriting last scores"""
		filepath=os.path.join(DATA_STORE,"Last7Delays.json")
		with open(filepath, 'w') as outfile:
			json.dump(delay_scores, outfile)
	except Exception as e:
		log.error(e)	
	return delay_scores


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
		av_delay=round((delaytotal/total_reported),2)
	else:
		av_delay='N/A'
	log.info(f'New cases reported on {sd:%d/%m%/%Y}: {total_reported} Av delay: {av_delay}')
	return {'date':sd,'total_reported':total_reported,'delay_total':delaytotal}


def newcases_by_area(last_update):
	""" new cases and delays by area"""
	delays={}
	for areacode in codes():
		log.debug(f'checking {areacode}')
		place=stored_names.get(areacode)
		if not place:
			continue
		q=DailyReport.objects.filter(areacode=areacode)
		sd=last_update
		lag=0
		delaytotal=0
		total_reported=0
		local_distro={}
		while lag<30:
			lag+=1
			total_dailyreported=0	
			try:
				report=q.get(specimenDate=sd-timedelta(lag),publag=lag)
				log.info(report.__dict__)
				newcases=report.dailycases-previous_total(report)
				total_dailyreported+=newcases
				delaytotal+=(lag*total_dailyreported)
				total_reported+=total_dailyreported
				if total_dailyreported != 0:
					local_distro[lag]=local_distro.get(lag,0)+total_dailyreported
				log.debug(f'lag: {lag}  total: {total_dailyreported}')
			except DailyReport.DoesNotExist:
				pass
		if total_reported:
			av_delay=round((delaytotal/total_reported),2)
		else:
			continue
			#av_delay='N/A'
		log.info(f'{place}: new cases: {last_update:%d/%m/%Y}: {total_reported} Av delay: {av_delay} Distribution: {local_distro}')
		delays[areacode]={'place':place,'total_reported':total_reported,'av_delay':av_delay, 'delay_total':delaytotal, 'distribution':local_distro}
	return delays
		
def delays_recent(start=date(2020,8,31)):
	codes=stored_names.keys()
	sd=start
	while sd < start+timedelta(12):
		series=[]
		lag=0
		total_delay=0
		total_cases=0
		while lag<15:
			date_total=0
			for areacode in codes:
				try:
					report=DailyReport.objects.get(areacode=areacode,specimenDate=sd,publag=lag)
					#previous=previous_total(report)
					newcases=report.add_cases
					total_cases+=newcases
					date_total+=newcases
					total_delay+=newcases*lag					
				except DailyReport.DoesNotExist as e:
					pass
				except DailyReport.MultipleObjectsReturned as e:
					log.error(e)
					log.error(f'Multiple objects: for {sd} lag {lag} in {areacode}')
			series.append((lag,date_total))
			lag+=1
		
		av_delay=round((total_delay/total_cases),2) if total_delay else None
		log.info(f'Date: {sd}: lag/case {series} av_delay: {av_delay}') 
		sd+=timedelta(1)
	

def list_delays(areacode):
	q=DailyReport.objects.filter(areacode=areacode).order_by('specimenDate','publag')
	for i in q:
		print(f'{i.specimenDate:%d/%m},{i.dailycases},{i.publag}')
	

def check_pubcases(codes=stored_names.keys()):
	last_update=date.today()
	n=0
	while n <30:
		new_cases(last_update-timedelta(n),codes=codes)
		n+=1
	
		
def previous_total(report):
	"""previous total cases - prior to given report"""
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
	
	
def summary_cases():
	"""total of cumulative cases by nation by specimen date"""
	today=date.today()
	n=0
	log.info('Cases published by specimen date')
	while n<10:
		sdate=today-timedelta(n)
		eng_cases=DailyCases.objects.filter(specimenDate=sdate,areacode__in=english).aggregate(Sum('dailyLabConfirmedCases'))['dailyLabConfirmedCases__sum']
		scot_cases=DailyCases.objects.filter(specimenDate=sdate,areacode__in=scottish).aggregate(Sum('dailyLabConfirmedCases'))['dailyLabConfirmedCases__sum']
		welsh_cases=DailyCases.objects.filter(specimenDate=sdate,areacode__in=welsh).aggregate(Sum('dailyLabConfirmedCases'))['dailyLabConfirmedCases__sum']
		n_irish_cases=DailyCases.objects.filter(specimenDate=sdate,areacode__in=nirish).aggregate(Sum('dailyLabConfirmedCases'))['dailyLabConfirmedCases__sum']
		
		log.info(f'{sdate:%d/%m/%Y} Cases: {eng_cases} (England)  {welsh_cases}(Wales)  {scot_cases}(Scotland)  {n_irish_cases}(N Ireland)')
		
		n+=1

#TOOLS

def duplicates():
	return DailyReport.objects.values('specimenDate','publag','dailycases','areacode').order_by().annotate(max_id=Max('id'), count_id=Count('id')).filter(count_id__gt=1)


def kill_dups():
	dups=duplicates()
	for dup in dups:
		DailyReport.objects.get(id=dup['max_id']).delete()


def date_range(q):
	"""unique dates in a range"""
	return [x['specimenDate'] for x in q.values('specimenDate').distinct()]

def refresh_increments():
	codes=stored_names.keys()
	for areacode in codes:
		log.info(f'Processing: {stored_names[areacode]}')
		q=DailyReport.objects.filter(areacode=areacode).order_by('specimenDate')
		dates=date_range(q)
		for sdate in dates:
			reports=q.filter(specimenDate=sdate).order_by('publag')			
			last_total=0
			last_lag=None
			for report in reports:
				lag=report.publag
				if last_lag==lag:
					log.error(f'Duplicate report: {report.__dict__}')
				daily=report.dailycases
				increment=daily-last_total
				log.debug(f'{sdate:%d-%m} lag{lag} total:{daily} incr {increment}')
				report.add_cases=increment
				report.save()
				last_total=daily
				last_lag=lag
	log.info('Completed refresh increments')
				
class England_Delays(Check_PHE):
	pass
	
	@property
	def filters(self):
		return ['areaType=nation']
		
	def __init__(self):
		self.api = Cov19API(filters=self.filters, structure=self.structure)
		try:
			self.get()
			
			self.table=pandas.DataFrame.from_dict(self.data['data'])
		except Exception as e:
			print(e)

	