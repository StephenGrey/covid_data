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
        print('parsing')
        print(row)
        post=CovidWeek()   
        post.areacode=row[0]
        post.areaname=row[1]
        datestring=row[2]
        post.date=self.fetchdate(datestring)
        post.weeklydeaths=row[3]
        post.totcumdeaths=row[4]
        post.weeklycases=row[5]
        post.totcumcases=row[6]
        post.estcasesweekly=row[7]
        print(post)
        print('saving')
        post.save()
    
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

