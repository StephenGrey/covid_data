from graph import phe_fetch, delays,model_calcs,phe_codes,ons_week
import os,json,logging
from .import_csv import DATA_STORE
from utils import time_utils
from .models import DailyCases, CovidScores #CovidWeek, DailyReport,
from datetime import timedelta,date
from django.db.models import Sum,Max,Count
log = logging.getLogger('api.graph.phe_deaths')
import configs
from configs import userconfig



RANGE=model_calcs.RANGE

class PHE_Deaths(phe_fetch.Fetch_API):

    @property
    def structure(self):
        return{
        "specimenDate": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newDeaths28DaysByPublishDate":"newDeaths28DaysByPublishDate",
        "newDeaths28DaysByDeathDate":"newDeaths28DaysByDeathDate",
        "cumDeaths28DaysByPublishDate":"cumDeaths28DaysByPublishDate",
        }
        
    def process(self):
        """pull the data district by district"""
        if self.update_check() or self.force_update:
            self.district_check() #pull all local data and regions
            self.fix() #fix data anomalies - e.g add in Bucks.
            
            self.save_all() #store a copy of the data
            
            
            self.ingest() #add data to models
            self.merge_scotland()
            self.count_deaths()
            self.calc_wave2_rates()
#			self.update_totals() #calculate weekly data
        else:
            log.info('PHE Deaths up to date')

    @property
    def update_check(self):
    	ck=check_Deaths()
    	ck.top()
    	self.latest_deaths=ck.latest_deaths
    	return ck._update

    def save_all(self):
        _date=self.latest_date_str #fetches date of latest published update
        filename=f"{_date}-PHE-deaths.json"
        filepath=os.path.join(DATA_STORE,filename)
        with open(filepath, 'w') as outfile:
            json.dump(self.data_all, outfile)
            
            
            
    def ingest(self,check=True):
    	"""ingest all the data"""
    	data=self.data_all
    	pubdate=time_utils.parseISO(self.api.last_update).date()
    	
    	counter=0
    	for item in data:
    		areacode=item['areaCode']
    		datestring=item['specimenDate']
    		_date=phe_fetch.fetchdate(datestring)
    		row,created=DailyCases.objects.get_or_create(specimenDate=_date,areacode=areacode)
    		row.areaname=item['areaName']
    		
    		deaths=item['newDeaths28DaysByDeathDate']
    		total_published_deaths=item['cumDeaths28DaysByPublishDate']
    		published_deaths=item['newDeaths28DaysByPublishDate']
    		#log.debug(f'{row.areaname}: {datestring}')			
    
    		if created:
    			row.deaths=deaths
    			row.total_published_deaths=total_published_deaths
    			row.published_deaths=published_deaths
    			row.save()
    			    		
    		if not created:
    			existing_deaths=row.deaths
    			existing_pubdeaths=row.published_deaths
    			existing_pubtotal=row.total_published_deaths
    			if deaths is not None or published_deaths is not None or total_published_deaths is not None:
    				""" update is there is some data and it has changed"""
    				if existing_deaths !=deaths or existing_pubtotal!=total_published_deaths or published_deaths !=existing_pubdeaths:
    					row.deaths=deaths
    					row.total_published_deaths=total_published_deaths
    					row.published_deaths=published_deaths
    					row.save()	
    		counter+=1
    		if counter%1000==0:
    			log.info(f'Processing row {counter}')
    	log.info(f'Processed: {counter} rows')
    
    	if self.latest_deaths:
    		configs.userconfig.update('PHE','england_total_deaths',str(self.latest_deaths))
    		
    		
    def output_place(self,place='Liverpool'):
    	q=DailyCases.objects.filter(areaname=place).order_by('specimenDate')
    	for case in q:
    		print(f'Date:{case.specimenDate:%d/%m} Deaths:{case.deaths} Published:{case.published_deaths} Total Pub:{case.total_published_deaths}')
    		
    		
    def deaths_range(self,_range=RANGE,place='Liverpool'):
    	return DailyCases.objects.filter(areaname=place,specimenDate__range=_range).aggregate(Sum('deaths'))['deaths__sum']
    	

    """ingest stored deaths publication """
    def open_file(self,path):
    	self.data = pandas.read_json(path, encoding= "utf-8")
    	
 
    def count_deaths(self):
    	"""update all the excess death rates for all districts"""
    	_today=date.today()
    	newwave=["2020-09-01",_today]
    	last30=[_today-timedelta(30),_today]
    	
    	for place in phe_codes.area_types.keys():
    		try:
    			i,created=CovidScores.objects.get_or_create(areaname=place)

    			wave2=self.deaths_range(_range=newwave,place=place)
    			last_month=self.deaths_range(_range=last30,place=place)
    			log.info(f'Place:{place} Wave2:{wave2} 30days:{last_month}')
    		
    			i.last_month_PHEdeaths=last_month
    			i.wave2_PHEdeaths=wave2
    			i.save()
    		except Exception as e:
    			log.error(f'Error with {place}')
    			log.error(e)
    		
    def calc_wave2_rates(self):
    	"""update wave2 rates for all districts"""
    	log.info('Beginning calc of wave2 rates')
    	for place in model_calcs.district_names():
    		i=CovidScores.objects.get(areaname=place)
    		wave2=i.wave2_PHEdeaths
    		wave2_rate=round(wave2/i.population*100000,1) if wave2 is not None and i.population else None
    		i.wave2_deathrate=wave2_rate
    		log.debug(f'Place: {place} Cases: {wave2} Rate:{wave2_rate}')
    		i.save()
    	log.info('Completed wave2 rate calculations')
 
    
    def merge_scotland(self):
    	"""add districts into health board"""
    	for board,districts in ons_week.health_boards.items():
    		board_score=CovidScores.objects.get(areaname=board)
    		wave2=0
    		last_month=0
    		for district in districts:
    			d_score=CovidScores.objects.get(areaname=district)
    			if d_score.wave2_PHEdeaths:
    				wave2+=d_score.wave2_PHEdeaths
    			if d_score.last_month_PHEdeaths:
    				last_month+=d_score.last_month_PHEdeaths
    		log.debug(f'board:{board} wave2:{wave2} last30:{last_month}')
    		board_score.wave2_PHEdeaths=wave2
    		board_score.last_month_PHEdeaths=last_month
    		board_score.save()


class check_Deaths(PHE_Deaths):
    
    def top(self):
    	PHEstored=configs.config.get('PHE')
    	if PHEstored:
    		self.England_deaths=PHEstored.get('england_total_deaths')
    	try:
    		self.api.filters=self.England_filter
    		self.api.latest_by="cumDeaths28DaysByPublishDate"
    		self.get()
    		self.latest_deaths=self.data.get('data')[0].get('cumDeaths28DaysByPublishDate')
    		if self.England_deaths == str(self.latest_deaths):
    			self._update=False
    		else:
    			self._update=True
    	except Exception as e:
    		log.debug(e)
    		log.info('Check PHE deaths failed - default to needs update')
    		self._update=True        
