# -*- coding: utf-8 -*- 
import os,json,requests,csv,pandas
from bs4 import BeautifulSoup as BS
from utils import time_utils
from .models import DailyCases,CovidWeek, DailyReport
from datetime import datetime,timedelta,date
import pytz
from contextlib import closing
from . import ons_week, model_calcs
from .import_csv import DATA_STORE,PandaImporter
from django.db.models import Max

import configs
from configs import userconfig

#pip install uk-covid19
from uk_covid19 import Cov19API
#https://github.com/publichealthengland/coronavirus-dashboard-api-python-sdk


URL="https://c19downloads.azureedge.net/downloads/json/coronavirus-cases_latest.json"
URL_CSV="https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv"
DASHBOARD="https://coronavirus.data.gov.uk/"
MSOA: "https://c19downloads.azureedge.net/downloads/msoa_data/MSOAs_latest.csv"

TIMEOUT=60
DATALOAD={}
AREACODE="E08000025"
AREA="Birmingham"

class NoContent(Exception):
    pass

class NoEntry(Exception):
    pass


class Check_PHE():
    def __init__(self):
        self.api = Cov19API(filters=self.filters, structure=self.structure)
        PHEstored=configs.config.get('PHE')
        if PHEstored:
            self.England_cases=PHEstored.get('england_total_cases')
            self.edition=PHEstored.get('latest_update')

        else:
            self.England_cases=None
        try:
            self.top()
        except Exception as e:
            print(e)
            print('Check PHE failed - default to needs update')
            self._update=True
            
    
    def top(self):
        """get latest total"""
        self.api.latest_by='cumCasesByPublishDate'
        self.get()
        self.latest_total=self.data['data'][0]['cumCasesByPublishDate']
        print(f'England latest total: {self.latest_total}')
        if self.latest_total:
            if self.England_cases:
                if int(self.England_cases)==self.latest_total:
                    if self.edition==self.latest_update:
                        print('Database up to date')
                        self._update=False
                        return False
                    else:
                        print(f'Database needs update: PHE latest: {self.latest_update}  Stored update:{self.edition}')
            userconfig.update('PHE','england_total_cases',str(self.latest_total))
        self._update=True
        return True
        
        
    @property
    def filters(self):
        """override to any filter"""
        return self.England_filter
        
    @property
    def structure(self):
        """override to any structure"""
        return self.cases_and_deaths
        
    def get(self):
        print('Fetching PHE cases from API')
        try:
            self.data=self.api.get_json()  # Returns a dictionary
        except Exception as e:
            print(e)
            print('Failed to download cases')
            
    @property
    def latest_update(self):
        return self.data.get('lastUpdate')

    @property
    def cases_and_deaths(self):
        return {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newCasesBySpecimenDate":"newCasesBySpecimenDate",
        "cumCasesBySpecimenDate":"cumCasesBySpecimenDate",
        }
    
    @property
    def England_filter(self):
        return ['areaType=nation','areaName=England']
        
    
    @property
    def local_filter(self):
        return ['areaType=ltla']

    @property
    def local_filter(self):
        return ['areaType=ltla']

    @property
    def updated(self):
        return self.api.last_update
        
    @property
    def newcases(self):
        return{
        "specimenDate": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
#        "newCasesByPublishDate": "newCasesByPublishDate",
#        "cumCasesByPublishDate": "cumCasesByPublishDate",
#        "newDeathsByDeathDate": "newDeathsByDeathDate",
#        "cumDeathsByDeathDate": "cumDeathsByDeathDate",
        "newCasesBySpecimenDate":"newCasesBySpecimenDate",
        "cumCasesBySpecimenDate":"cumCasesBySpecimenDate"
        }
        

    def save(self):
        filename=f"{date.today()}-PHE-cases.json"
        filepath=os.path.join(DATA_STORE,filename)
        with open(filepath, 'w') as outfile:
            json.dump(self.data, outfile)

class LocalLatest(Check_PHE):
    def __init__(self):
        self.api = Cov19API(filters=self.local_filter, structure=self.structure)
        self.api.latest_by='cumCasesByPublishDate'
        self.get()


class Fetch_API(Check_PHE):
	def __init__(self,force_update=False):
		self.today=date.today()
		self.api = Cov19API(filters=self.filters, structure=self.structure)
		self.edition=None
		self.sequences=['ltla','region']
		#self.api.latest_by='cumCasesBySpecimenDate' - this fetches only latest cases
		#self.fetch - get
		self.data_all=[]
		self.force_update=force_update
		
		
	def fetch(self):
		for sequence in self.sequences:
			self.api.filters=[f'areaType={sequence}']
			print(f'SEQUENCE: {sequence}')
			self.get()  #get local data			
			self.data_all +=self.data.get('data')
		self.edition=self.latest_update
						
	def fix(self):
		#get Bucks data
		self.api.filters=['areaType=utla', 'areaName=Buckinghamshire']
		self.get()
		bucks=self.data.get('data')
		fixed=[]
		for row in bucks:
			print(row)
			row['areaCode']='E06000060'
			fixed.append(row)
		self.data_all+=fixed
		print('Fixed wrong areacode and added Bucks in PHE local data')
	
	@property
	def filters(self):
		"""override to any filter"""
		return self.local_filter
		
	@property
	def structure(self):
		"""override to any structure"""
		return self.newcases
	

	def process(self):
		if self.update_check() or self.force_update:
			self.fetch() #pull all local data and regions
			self.fix() #fix data anomalies - e.g add in Bucks.
			self.ingest() #add data to models
			self.update_totals() #calculate weekly data
			self.save() #store a copy of the data
		else:
			print('PHE cases up to date')
	
	
	def areacodes():
		output=set()
		for x in zz.data['data']:
			output.add(x['areaCode'])
		return output

	def _test_ingest(self,check=True):
		"""ingest all the data"""
		data=self.data_all
		pubdate=self.edition
		
		counter=0
		for item in data:
			areacode=item['areaCode']
			datestring=item['specimenDate']
			_date=fetchdate(datestring)
			row,created=DailyCases.objects.get_or_create(specimenDate=_date,areacode=areacode)
			row.areaname=item['areaName']
			daily=item['newCasesBySpecimenDate']
			total=item['cumCasesBySpecimenDate']
			row,created=DailyReport.objects.get_or_create(specimenDate=date,publag=lag)
			lag=(time_utils.parseISO(self.edition).date()-_date.date()).days
			print(f'{row.areaname}: Pubdate{pubdate}, SpecimenDate {_date.date},  Lag: {lag}')
			
			if counter==10:
				break
			
#			row,created=DailyReport.objects.get_or_create(specimenDate=date,publishDate=pubdate,areacode=item['areaCode'])
#			lag=(time_utils.parseISO(self.edition).date()-_date.date()).days#
#			print(lag)
 		
 		
	def ingest(self,check=True):
		"""ingest all the data"""
		data=self.data_all
		pubdate=self.edition
		
		counter=0
		for item in data:
			datestring=item['specimenDate']
			_date=fetchdate(datestring)
			row,created=DailyCases.objects.get_or_create(specimenDate=_date,areacode=item['areaCode'])
			row.areaname=item['areaName']
			print(f'{row.areaname}: {datestring}')
			daily=item['newCasesBySpecimenDate']
			total=item['cumCasesBySpecimenDate']
			
			if created:
				row.dailyLabConfirmedCases=daily
				row.totalLabConfirmedCases=total
				row.save()
			if not created:
				existing_daily=row.dailyLabConfirmedCases
				existing_total=row.totalLabConfirmedCases
				if existing_daily !=daily or existing_total!=total:
					print(f'Updating {row.areaname} on {datestring}: Daily: {existing_daily} to {daily}  Total: {existing_total} to {total}')
					row.dailyLabConfirmedCases=daily
					row.totalLabConfirmedCases=total
					row.save()
			counter+=1
			if counter%100==0:
				print(f'Processing row {counter}')
		print(f'Processed: {counter} rows')

		if self.edition:
			configs.userconfig.update('PHE','latest_update',self.edition)
	
	def save(self):
		filename=f"{date.today()}-PHE-cases.json"
		filepath=os.path.join(DATA_STORE,filename)
		with open(filepath, 'w') as outfile:
			json.dump(self.data_all, outfile)
		
	def update_totals(self):
		update_weekly_cases('England')
		update_weekly_cases('Northern Ireland')
		update_weekly_cases('Wales')
		
	def update_check(self):
		return check()
		
		
			
		
#		
#		PHEstored=configs.config.get('PHE')
#		if PHEstored:
#			self.last_update=PHEstored.get('latest_cases')
#			if self.last_update:
#				if self.edition == self.last_update:
#					return False
#		return True

#	def fetch(self,url=URL):
#		""" get the latest cases data"""
#		print('downloading latest PHE case data')
#		self.data=lookup_json(url)
#		
#		self.edition=self.data['metadata']['lastUpdatedAt']
#		print(f'Last updated on {self.edition}')

	def sequence_ingest(self,sequence):
		"""ingest from a particular sequence"""
		data=self.data
		
		counter=0

		for item in data[sequence]:
			datestring=item['specimenDate']
			date=fetchdate(datestring)
			row,created=DailyCases.objects.get_or_create(specimenDate=date,areacode=item['areaCode'])
			row.areaname=item['areaName']
			row.dailyLabConfirmedCases=item['dailyLabConfirmedCases']
			row.totalLabConfirmedCases=item['totalLabConfirmedCases']
			row.changeInDailyCases=item['changeInDailyCases']
			row.dailyTotalLabConfirmedCasesRate=item['dailyTotalLabConfirmedCasesRate']
			row.previouslyReportedDailyCases=item['previouslyReportedDailyCases']
			row.previouslyReportedTotalCases=item['previouslyReportedTotalCases']
			row.changeInTotalCases=item['changeInTotalCases']
			row.save()
			counter+=1
		print(f'Processed: {counter} rows')


class OLDCheck_PHE():
	def __init__(self):
		PHEstored=configs.config.get('PHE')
		if PHEstored:
			self.England_cases=PHEstored.get('england_total_cases')
		else:
			self.England_cases=None
		self.top()
		
	def top(self,url=URL_CSV):
		"""get lastest England total"""
		
		with closing(requests.get(url, stream=True)) as r:
			f = (line.decode('utf-8') for line in r.iter_lines())
			reader = csv.reader(f, delimiter=',', quotechar='"')
			fields=next(reader,None)
			england=next(reader,None)
			self.latest_total=england[7]
			print(f'England latest total: {self.latest_total}')
			
		if True:
			if self.latest_total:
				if self.England_cases:
					if str(self.England_cases) ==self.latest_total:
						print('nothing new here')
						self._update=False
						return False
				userconfig.update('PHE','england_total_cases',str(self.latest_total))
				self._update=True
				return True
				
#			for count, row in enumerate(reader, start=1):
#				print(row[7])
#				if count == 1:
#					break

class Fetch_PHE(PandaImporter):
	"""fetch PHE cases for England and Wales from CSV"""
	
	def __init__(self):
		self.today=date.today()
		self.edition=None
		self.fetch()
		self.fix()
		self.sequences=['ltla', 'nation', 'region', 'utla']
		
	def process(self):
		"""ingest cases into database & update weekly totals"""
		if self.update_check():
			self.ingest_all()
			self.update_totals()
		else:
			print('PHE cases up to date')
	
	def district_codes(self):
		return sorted([z for z in self.data['Area code'].unique()])

	
	def ingest_all(self):
		"""pull all daily cases from all PHE areas"""
		for place in self.district_codes():
			self.sequence_ingest(place)
		if self.edition:
			configs.userconfig.update('PHE','latest_cases',self.edition)

	def save(self):
		filename=f"{date.today()}-PHE-cases.csv"
		filename2=f"{date.today()}-PHE-cases.json"
		filepath=os.path.join(DATA_STORE,filename)
		filepath2=os.path.join(DATA_STORE,filename2)
		self.data.to_csv(filepath)
		self.data.to_json(filepath2)
#		with open(filepath, 'w') as outfile:
#			json.dump(self.data, outfile)
		
	def update_totals(self):
		update_weekly_cases('England')


	def update_check(self):
		PHEstored=configs.config.get('PHE')
		if PHEstored:
			self.last_update=PHEstored.get('latest_cases')
			if self.last_update:
				if self.edition == self.last_update:
					return False
		return True

	@property
	def total_cases(self):
		return self.data[self.data['Area type']=='utla']['Daily lab-confirmed cases'].sum()
	
	@property
	def latest_samples(self):
		return self.data['Specimen date'].max()
	
	def fetch(self,url=URL):
		""" get the latest cases data"""
		print('downloading latest PHE case data')
#		self.data=lookup_json(url)
		self.fetch_csv() #JSON discontinued; switched back to CSV
		self.edition=self.latest_samples
		print(f'Last samples from {self.edition}')

	def fetch_csv(self,url=URL_CSV):
		path=os.path.join(DATA_STORE,'PHE_latestcases.csv')
		res=requests.get(url)
		with open(path, 'wb') as f:
			f.write(res.content)
		self.open_csv(path)

	def fix(self):
		self.data.loc[self.data['Area name']=='Buckinghamshire','Area code']='E06000060'
		print('Fixed wrong areacode for Bucks in PHE data')

	def open_csv(self,f):
		self.data=pandas.read_csv(f, encoding= "iso-8859-1")

	def sequence_ingest(self,areacode):
		"""ingest from a particular areacode"""
		data=self.data[self.data['Area code']==areacode]
		areaname=data['Area name'].unique().item()
		print(f'Ingesting cases from {areacode}: {areaname}')
		
		counter=0
		for day in data['Specimen date']:
			date=fetchdate(day)
			row,created=DailyCases.objects.get_or_create(specimenDate=date,areacode=areacode)
			this_day=data[data['Specimen date']==day]
			row.areaname=areaname 
			#add head(1) (faster than unique() ) to deal with some areas returned twice as part of both UTLA AND LTLA sequences
			row.dailyLabConfirmedCases=this_day['Daily lab-confirmed cases'].head(1).item()
			row.totalLabConfirmedCases=this_day['Cumulative lab-confirmed cases'].head(1).item()
			row.save()
			counter+=1
		print(f'Processed: {counter} rows')



def check():
    ck=Check_PHE()
    return ck._update

def check_and_download():
    if check():
        f=Fetch_PHE()
        if f.update_check():
            print('Saving latest PHE cases')
            f.save()
    else:
        print('No need to download')


def update_weekly_cases(nation):
    q=CovidWeek.objects.filter(nation=nation)
    for place in q.values('areacode','areaname').distinct():
        areacode=place['areacode']
        area=place['areaname']
        if areacode and area:
            update_weekly_total(areacode=areacode,areaname=area)

def update_weekly_total(areacode=AREACODE,areaname=AREA):
    """add up all daily cases into week calculation"""
    start,stop=model_calcs.RANGE_WEEK
    print(f'Processing {areaname}')
    for week in range(start,stop+1):
        end_day=ons_week.week(week)
        
        week_total=weekly_total(end_day,areacode=areacode,areaname=areaname)
        print(f'{areaname}: Weektotal for week number {week} ending {end_day}: {week_total}')
        
        if week_total is not None:
            try:
                stored,created=CovidWeek.objects.get_or_create(areacode=areacode,week=week)
                #print(stored.weeklycases)
                if stored.weeklycases != week_total:
                    print(f'{areaname}: updating week {week} from {stored.weeklycases} to {week_total}')
                    stored.weeklycases=week_total
                    stored.areaname=areaname
                    stored.save()
                if created:
                    stored.nation=ons_week.nation[areacode]
                    stored.areaname=areaname
                    print(f'Created new entry for week {week} for {areaname}')
                    stored.week=week
                    stored.save()
            except Exception as e:
                print(e)
                print(f'No data stored for week {week}')
        else:
            print(f'Bypassing {areaname} - no data')

def weekly_total(end_day,areacode=AREACODE,areaname=AREA):
    if True:
        week_total=0
        for day in range(6,-1,-1):
            date=end_day-timedelta(day)
            try:
                entry=DailyCases.objects.get(areacode=areacode,specimenDate=date)
                week_total+=entry.dailyLabConfirmedCases
            except:
                #print(f'No entry for {date}')
                pass
    return week_total
                
def sum_cases(nation='England'):
    """add up total cases for a nation - for integrity checks"""
    _sum=0
    for _code in ons_week.stored_names:
        if ons_week.nation[_code]==nation:
            place=ons_week.stored_names[_code]
            _total=DailyCases.objects.filter(areaname=place).aggregate(Max('totalLabConfirmedCases')).get('totalLabConfirmedCases__max')
            if _total:
                _sum +=_total
            else:
               print(f'No total for {place}')
    return _sum

def check_sum_cases(nation='England'):
    """check total data"""
    ck=LocalLatest()
    fail=False
    data=ck.data.get('data')
    latest={}
    
    #check latest data matches stored data for nation
    for i in data:
        _code=i['areaCode']
        latest[_code]=i
        try:
            _nation=ons_week.nation[_code]
        except Exception as e:
            print(e)
            print(i['areaName'])
            continue
        if _nation==nation:
            if _code in ons_week.stored_names:
                place=ons_week.stored_names[_code]
                _total=DailyCases.objects.filter(areaname=place).aggregate(Max('totalLabConfirmedCases')).get('totalLabConfirmedCases__max')
                _latest=i['cumCasesByPublishDate']
                if _total !=_latest:
                    print(f'Mismatch: {place} Latest total{_latest} != stored {_total}')
                    fail=True
                else:
                    #print(f'{place} up to date')
                    pass
            else:
                place=i['areaName']
                print(f'{place} not counted / not in TR tally')
                
    sumtotal=0
    for _code in ons_week.stored_names:
        if ons_week.nation[_code]==nation:
            i=latest.get(_code)
            if i:
                _latest=i['cumCasesByPublishDate']
                _total=DailyCases.objects.filter(areacode=_code).aggregate(Max('totalLabConfirmedCases')).get('totalLabConfirmedCases__max')
                if _latest!=_total:
                    print(f'Mismatch: {_code} Latest total{_latest} != stored {_total}')
                else:
                    if latest:
                        sumtotal +=_latest
            else:
                print(f'Missing place {_code} in PHE published cases')
    print(f'Sum total of stored names for {nation} is {sumtotal}')
    
    return fail

#DATALOAD=main()

def process(data):
	data=main(eg)
	latest=data['ltlas']#list of latest entries - lower teir
	latest_upper_tier=data['utlas'] # upper tier
	metadata=data['metadata']
	daily_countrylevel=data['countries'] #just England
	regions=data['regions'] #English regions
	bigtotal=['dailyRecords']

def max_week():
	return CovidWeek.objects.aggregate(Max('week')).get('week__max')

def name_index():
	q=DailyCases.objects.values('areacode','areaname').distinct()
	_i={}
	for place in q:
		areacode=place['areacode']
		area=place['areaname']
		_i[areacode]=area
	return _i

def lookup_json(url):
    """fetch and decode json from an api"""
    session=requests.Session()
    json_res=get_api_result(session,url)
    try:
        content=json.loads(json_res)
        return content
    except:
        raise NoContent
    
    
def get_api_result(session,url):
    """return content of a get request"""
    try:
        res=session.get(url,timeout=TIMEOUT)
        if res.status_code == 404:
            raise NotFound("URL {} not found".format(url))
    except Exception as e:
        print(e)
        return None
    return res.content



def fetchdate(datestring):
        try:
            if not datestring:
                raise NullDate
            date=datetime.strptime(datestring,'%Y-%m-%d')
#            date=iso8601.parse_date(datestring) -- convert a string in ISO8601
            date=timeaware(date)
            #print(datestring,date)
        except ValueError:
            raise NullDate
        return date

        
def timeaware(dumbtimeobject):
    return pytz.timezone("GMT").localize(dumbtimeobject)
#Mac / Linux stores all file times etc in GMT, so localise to GMT


def ingest_cases(data):
	count=0
	print('Checking for new data')
	try:
		for index,row in data.iterrows():
			try:
				count+=1
				if count%100==0:
					print(count)
				i,created=DailyCases.objects.get_or_create(areacode=row['Area code'], specimenDate=fetchdate(row['Specimen date']))
				i.dailyLabConfirmedCases = row['Daily lab-confirmed cases']
				i.totalLabConfirmedCases = row['Cumulative lab-confirmed cases']
			except DailyCases.DoesNotExist:
				print('entry does not exist')
			
	finally:
		print(count)
			


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
	def __init__(self,filepath):
		self.filepath=filepath
		self.open_csv(self.filepath)
		self.pubdate=fetchdate(os.path.basename(filepath)[:10]).date()
		print(f'Processing case data published {self.pubdate}')
	
	def open_csv(self,path):
		self.data = pandas.read_csv(path, encoding= "utf-8") 
		
	def ingest_all(self):
		"""pull all daily cases from all PHE areas"""
		for place in self.district_codes():
			self.sequence_ingest(place)

			
	def sequence_ingest(self,areacode):
		"""ingest from a particular areacode"""
		data=self.data[self.data['Area code']==areacode]
		areaname=data['Area name'].unique().item()
		print(f'Ingesting cases from {areacode}: {areaname}')
		
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
			lag=(self.pubdate-date.date()).days
			rows=DailyReport.objects.filter(areacode=areacode,specimenDate=date).order_by('-specimenDate')
			if rows:
				lastentry=rows[0]
				if lastentry.dailycases !=cases:
					print('mismatch')
					row=DailyReport.objects.filter(areacode=areacode,specimenDate=date,publag=lag)
					row.dailycases=cases
					row.save()
				else:
					pass
			else:
				row=DailyReport(areacode=areacode,specimenDate=date,publag=lag)
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
			

#		datestring=item['specimenDate']
#		_date=fetchdate(datestring)
			
#			row.areaname=areaname 
#			#add head(1) (faster than unique() ) to deal with some areas returned twice as part of both UTLA AND LTLA sequences
#			row.dailyLabConfirmedCases=this_day['Daily lab-confirmed cases'].head(1).item()
#			row.totalLabConfirmedCases=this_day['Cumulative lab-confirmed cases'].head(1).item()
#			row.save()
#			counter+=1
#		print(f'Processed: {counter} rows')


#			row,created=DailyCases.objects.get_or_create(specimenDate=_date,areacode=areacode)
#			row.areaname=item['areaName']
#			daily=item['newCasesBySpecimenDate']
#			total=item['cumCasesBySpecimenDate']
#			row,created=DailyReport.objects.get_or_create(specimenDate=date,publag=lag)
#			lag=(time_utils.parseISO(self.edition).date()-_date.date()).days
#			print(f'{row.areaname}: Pubdate{pubdate}, SpecimenDate {_date.date},  Lag: {lag}')
#			
#			if counter==10:
#				break
#			
#			row,created=DailyReport.objects.get_or_create(specimenDate=date,publishDate=pubdate,areacode=item['areaCode'])
#			lag=(time_utils.parseISO(self.edition).date()-_date.date()).days#
#			print(lag)

    

