from graph import phe_fetch, delays,model_calcs
import os,json,logging
from .import_csv import DATA_STORE
from utils import time_utils
from .models import DailyCases,CovidWeek, DailyReport
log = logging.getLogger('api.graph.phe_deaths')


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
        if True: #self.update_check() or self.force_update:
            self.district_check() #pull all local data and regions
            self.fix() #fix data anomalies - e.g add in Bucks.
            self.save_all() #store a copy of the data
            self.ingest() #add data to models
#			self.update_totals() #calculate weekly data
        else:
            log.info('PHE Deaths up to date')


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
    			row.published_deaths=pubished_deaths
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
    
    	if self.edition:
    		configs.userconfig.update('PHE','latest_deaths_update',self.edition)
    		
    		
    		
    def output_place(self,place='Liverpool'):
    	q=DailyCases.objects.filter(areaname=place).order_by('specimenDate')
    	for case in q:
    		print(f'Date:{case.specimenDate:%d/%m} Deaths:{case.deaths} Published:{case.published_deaths} Total Pub:{case.total_published_deaths}')
    		
    		
    def deaths_range(self,_range=RANGE,place='Liverpool'):
    	q=DailyCases.objects.filter(areaname=place,specimenDate__range=_range).order_by('specimenDate')
    	_total=0
    	for case in q:
    		if case.deaths:
    			_total+=case.deaths
    	print(_total)
    	
    	
    

    """ingest stored deaths publication """
    def open_file(self,path):
    	self.data = pandas.read_json(path, encoding= "utf-8")
    	
    	
