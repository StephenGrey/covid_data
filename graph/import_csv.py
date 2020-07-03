# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from .models import CovidWeek
from datetime import datetime
import csv,pytz, os 
#import ast, iso8601
#import json, collections


class BadPath(Exception):
    pass

class NullDate(Exception):
    pass

class Importer:
    def __init__(self,f,maxloop=1000000):
        print('parsing')
        if not os.path.exists(f) or f is None:
            raise BadPath
        self.main(f,maxloop)
        print(CovidWeek.objects.all())
        
    def main(self,path,maxloop):
        with open(path) as f:
            reader = csv.reader(f)
            #first line is column headers
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