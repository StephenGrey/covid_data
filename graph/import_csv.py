# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from .models import CovidWeek,AverageWeek,CovidScores
from datetime import datetime
import csv,pytz, os, requests, codecs, pandas, io
from contextlib import closing

DATA_STORE=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../data'))




#import ast, iso8601
#import json, collections
#pop estimates 2020: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/localauthoritiesinenglandtable2
##import pandas as pd
#import io
#import requests
#url="https://raw.githubusercontent.com/cs109/2014_data/master/countries.csv"
#s=requests.get(url).content
#c=pd.read_csv(io.StringIO(s.decode('utf-8')))

#sorted([int(z[5:]) for z in c['week-number'].unique()])



class PandaImporter():
    def __init__(self, data=None):
        self.data=data
        self.edition=None
        self.download_url=None
        
    def fetch(self,url):
        self.session=requests.Session()
        try:
            resp=self.session.get(url)
            if resp.status_code == 404:
                raise NotFound("URL {} not found".format(url))
            raw=resp.content
        except requests.ConnectionError as e:
            print(e)
            return 
        except Exception as e:
            print(e)
            return
        self.data=pandas.read_csv(io.StringIO(raw.decode('utf-8')))
        
    
    def open_csv(self,path):
        self.data = pandas.read_csv(path, encoding= "utf-8") 
        
    def open_excel(self,path,sheet_name="Table 1",skiprows=0):
        self.data=pandas.read_excel(path,sheet_name=sheet_name,skiprows=skiprows).dropna() # covid deaths
        
    def parse(self):
        pass
        

class BadPath(Exception):
    pass

class NullDate(Exception):
    pass


url = "http://download-and-process-csv-efficiently/python.csv"




class URLImporter:
    def __init__(self,url,maxloop=1000000):
        print('parsing')
        self.session=requests.Session()
        self.main(url,maxloop)	
    
    def main(self,url,maxloop):
        with closing(self.session.get(url, stream=True)) as r:
            
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            #text = r.iter_lines()
            row=next(reader)
            counter=0
            print('Column headers: {}'.format(row))
            while row:
                try:
                    counter+=1
                    if counter>maxloop:
                        break
                    row=next(reader,None) # Don't raise exception if no line exists                
                    print(row)
                    if not row:
                        break
                    self.parserow(row)
                except Exception as e:
                    print('Error after reached row '+str(counter))
                    print(e)
                    
            # print(vars(post))
            print(str(counter)+' lines parsed')
        
    def parserow(self,row):
        pass
    


class Importer:
    def __init__(self,f,maxloop=1000000):
        print('parsing')
        if not os.path.exists(f) or f is None:
            raise BadPath
        self.main(f,maxloop)
        #print(CovidWeek.objects.all())
        
    def main(self,path,maxloop):
        with open(path) as f:
            reader = csv.reader(f)
            #first line is column headers
            row=next(reader)
            counter=0
            print('Column headers: {}'.format(row))
            self.columns=row
            while row:
                try:
                    counter+=1
                    if counter>maxloop:
                        break
                    row=next(reader,None) # Don't raise exception if no line exists                
                    print(row)
                    if not row:
                        break
                    self.parserow(row)
#                except NullDate as e:
#                    continue
                except Exception as e:
                    print('Error after reached row '+str(counter))
                    print(e)
                    
            # print(vars(post))
            print(str(counter)+'  posts added to database')
    
    
    def parserow(self,row):
#area_code,areaname,date,weekly_deaths,cum_deaths,weekly_cases,cum_cases,est_cases_weekly
        post=CovidWeek()
        post.nation=row[0]   
        post.areacode=row[1]
        post.areaname=row[2]
        datestring=row[3]
        post.date=self.fetchdate(datestring)
        
        weeklyd=row[4]
        if weeklyd:
            post.weeklydeaths=weeklyd
        else:
            post.weeklydeaths=None
        
        totd=row[5]
        if totd:
            post.totcumdeaths=totd
        else:
            post.totcumdeaths=None
        
        post.weeklycases=row[6]
        post.totcumcases=row[7]
        
        estc=row[8]
        if not estc:
            post.estcasesweekly=None
        else:
        	post.estcasesweekly=estc
        print('saving')
        try:
            post.save()
        except Exception as e:
            print(e)
            print(row)
            
    
    def fetchdate(self,datestring):
        print(datestring)
        try:
            if not datestring:
                raise NullDate
            date=datetime.strptime(datestring,'%d/%m/%Y')
#            date=iso8601.parse_date(datestring) -- convert a string in ISO8601
            date=timeaware(date)
            #print(datestring,date)
        except ValueError:
            raise NullDate
        return date

        
def timeaware(dumbtimeobject):
    return pytz.timezone("GMT").localize(dumbtimeobject)
#Mac / Linux stores all file times etc in GMT, so localise to GMT


class JustCases(Importer):
    def parserow(self,row):
        try:
            areacode=row[1]
            areaname=row[2]
            datestring=row[3]
            weeklycases=row[6]
            date=self.fetchdate(datestring)
            try:
                post=CovidWeek.objects.get(areacode=areacode,areaname=areaname,date=date)
                if post.weeklycases != weeklycases:
                    print(f'updating {areaname} date: {datestring} from {post.weeklycases} to {weeklycases}')
                    post.weeklycases=weeklycases
                    post.save()
            except:
                pass
        except Exception as e:
            print('error')
            print(e)
            

class AddNation(Importer):
	
	def parserow(self,row):
		try:
			areacode=row[0]
			district=row[1]
			nation=row[2]
			print(f'Parsing: Area: {district} Nation: {nation}')
			entries=CovidWeek.objects.filter(areacode=areacode)
			for e in entries:
				e.nation=nation
				e.save()
		except Exception as e:
			print(e)
#        post.save()

class AddAverages(Importer):
	#Local Authority Code,Local Authority Name,Week Number,Place of occurrence,Five year average number of deaths
	def parserow(self,row):
		try:
			wk, created = AverageWeek.objects.get_or_create(
			week=row[2],
			areacode=row[0]
			)
			location=row[3]
			print(f'Parsing: Area: {row[1]}')
			av=row[4]
			if location=='Hospital':
				wk.weeklyhospitaldeaths=av
			elif location=='Elsewhere':
				wk.weeklyelsewheredeaths=av
			elif location=='Hospice':
				wk.weeklyhospicedeaths=av
			elif location=='Other communal establishment':
				wk.weeklyothercommunaldeaths=av
			elif location=='Care home':
				wk.weeklycarehomedeaths=av
			elif location=='Home':
				wk.weeklyhomedeaths=av
			wk.save()
		except Exception as e:
			print(e)
			
	def total_averages(self):
		for wk in AverageWeek.objects.all():
			try:
				_sum=sum(filter(None,[wk.weeklyhospitaldeaths,wk.weeklyelsewheredeaths,wk.weeklyhospicedeaths,wk.weeklyothercommunaldeaths,wk.weeklycarehomedeaths,wk.weeklyhomedeaths]))
				wk.weeklyalldeaths=_sum
				wk.save()
			except Exception as e:
				print(e)
				print(wk.__dict__)
				
				
def merge_averages(districts2merge,target):
	"""merge averages for some areacodes into other areacode"""
	
	for week in range(1,54):
		q=AverageWeek.objects.filter(week=week,areacode__in=districts2merge)
		t,created=AverageWeek.objects.get_or_create(week=week,areacode=target)
		if created:
			print(f'Created average data for {target} for week{week}')
		t.weeklyhospitaldeaths=sum([i.weeklyhospitaldeaths for i in q])
		t.weeklyelsewheredeaths=sum([i.weeklyelsewheredeaths for i in q])
		t.weeklyhospicedeaths=sum([i.weeklyhospicedeaths for i in q])
		t.weeklyothercommunaldeaths=sum([i.weeklyothercommunaldeaths for i in q])
		t.weeklyhomedeaths=sum([i.weeklyhomedeaths for i in q])
		t.weeklycarehomedeaths=sum([i.weeklycarehomedeaths for i in q])
		t.weeklyalldeaths=sum([i.weeklyalldeaths for i in q])
		t.save()

class AddPop(Importer):
	#areacode,areaname,type,population2019
	def parserow(self,row):
		try:
			print(row)
			areacode=row[0]
			district=row[1]
			population=int(row[3])
			print(f'Parsing: Area: {district} pop {population}')
			
			e,created=CovidScores.objects.get_or_create(areaname=district)
			
			e.population=population
			e.save()

		except Exception as e:
			print(e)
			
class AddRegions(PandaImporter):
	def __init__(self, filepath=None):
		self.filepath=filepath
	
	@property
	def regions(self):
		return [x for x in self.data['AreaCode'].values]
	
	def process(self):
		self.open_excel(self.filepath,sheet_name="ALLDEATHS")
		
		for region in self.regions:
			row=self.data[(self.data['AreaCode']==region)]
			self.parserow(row)
		print('Added England and Wales regions total deaths to average figures')

	def parserow(self,row):
		print(row)
		if True:
			areacode=row['AreaCode'].item()
			for week in range(1,53):
				deaths=int(row[week])
				wk, created = AverageWeek.objects.get_or_create(
				week=week,
				areacode=areacode
				)
				wk.weeklyalldeaths=deaths
				wk.weeklyhospitaldeaths=None
				wk.weeklyelsewheredeaths=None
				wk.weeklyhospicedeaths=None
				wk.weeklyothercommunaldeaths=None
				wk.weeklycarehomedeaths=None
				wk.weeklyhomedeaths=None
				wk.save()
				print(f'Added: {areacode}: week{week} av deaths{deaths} created?:{created}')
#		except Exception as e:
#			print(e)

def total_averages():
	if True:	
		for wk in AverageWeek.objects.all():
			try:
				_sum=sum(filter(None,[wk.weeklyhospitaldeaths,wk.weeklyelsewheredeaths,wk.weeklyhospicedeaths,wk.weeklyothercommunaldeaths,wk.weeklycarehomedeaths,wk.weeklyhomedeaths]))
				wk.weeklyalldeaths=_sum
				wk.save()
			except Exception as e:
				print(e)
				print(wk.__dict__)
