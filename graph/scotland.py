import requests,json,csv,pandas,os
from datetime import datetime
from bs4 import BeautifulSoup as BS
from .ons_week import week as ons_week,sunday,stored_names,nation,scotcode
from datetime import timedelta
from .models import CovidWeek, DailyCases, AverageWeek
from .import_csv import URLImporter,PandaImporter,timeaware
from .model_calcs import update_cum_district_death,DATA_STORE
from .ons_fetch import update_row
from .phe_fetch import update_weekly_total

import configs
from configs import userconfig

INFO_URL="https://www.nrscotland.gov.uk/statistics-and-data/statistics/statistics-by-theme/vital-events/general-publications/weekly-and-monthly-data-on-births-and-deaths/deaths-involving-coronavirus-covid-19-in-scotland/related-statistics"

DEATHS_URL='https://www.nrscotland.gov.uk/files//statistics/covid19/weekly-deaths-by-date-health-board-location.xlsx'

CASES_URL="https://statistics.gov.scot/slice/observations.csv?&dataset=http%3A%2F%2Fstatistics.gov.scot%2Fdata%2Fcoronavirus-covid-19-management-information&http%3A%2F%2Fpurl.org%2Flinked-data%2Fcube%23measureType=http%3A%2F%2Fstatistics.gov.scot%2Fdef%2Fmeasure-properties%2Fcount&http%3A%2F%2Fstatistics.gov.scot%2Fdef%2Fdimension%2Fvariable=http%3A%2F%2Fstatistics.gov.scot%2Fdef%2Fconcept%2Fvariable%2Ftesting-cumulative-people-tested-for-covid-19-positive"

"""

Info and links:
https://www.nrscotland.gov.uk/statistics-and-data/statistics/statistics-by-theme/vital-events/general-publications/weekly-and-monthly-data-on-births-and-deaths/deaths-involving-coronavirus-covid-19-in-scotland

Deaths data file downloaded:  (Data updated every Wednesday)

Weekly deaths by date of occurrence, health board and location:
https://www.nrscotland.gov.uk/files//statistics/covid19/weekly-deaths-by-date-council-area-location.zip"

#https://www.gov.scot/publications/coronavirus-covid-19-trends-in-daily-data/
	
#data.columns=['Week of occurrence','Health Board','Location of death','Cause of Death','deaths']
#load average deaths: https://www.nrscotland.gov.uk/files//statistics/covid19/weekly-deaths-by-date-health-board-location-15-19.zip


Footnotes:					
1) figures are provisional and subject to future changes					
2) Weeks run from Monday to Sunday and are based on the ISO8601 international standard for week numbering. Note that weeks at the beginning and end of a year can overlap with the previous and subsequent year, so counts may not sum to annual totals published elsewhere.			
3) Other institutions include clinics, medical centres, prisons and schools.					
					
"""
class Scot_Importer(PandaImporter):
    
    def update_check(self):
        scotupdate=configs.config.get('Scotland')
        if scotupdate:
            self.last_update=scotupdate.get('latest_deaths')
        else:
            self.last_update=None
        
        res=requests.get(INFO_URL)
        if res:
            html=res.content
            soup=BS(res.content, 'html.parser')
            el=soup.table.tbody.contents[3].td.next.next.next.text
            target="Weekly deaths by date of occurrence, health board and location"
            if target in el:
                print("Found target: latest Scotland weekly deaths data")
                self.edition=el[el.find('(')+1:el.find(')')]
                print(f"Last update: {self.edition}")
                #datetime. strptime(self.edition, '%d %B %Y')
        
        if self.edition and self.edition==self.last_update:
            print('Up to date')
            return False
        else:
            print('Update available')
            return True
            
    def process(self,f=DEATHS_URL):
        self.fetch_excel(url=f,skiprows=2,sheet_name="Data")
        self.fix()
        self.parse()
        
    def fetch_excel(self,url=DEATHS_URL,skiprows=2,sheet_name="Data"):
        f=requests.get(url)
        xl=f.content if f else None
        self.data=pandas.read_excel(xl,sheet_name=sheet_name,skiprows=skiprows)
        return self.data
        
    def fix(self):
        self.data=self.data[self.data.columns[:5]].dropna()
        self.data['Deaths'] = self.data['Deaths'].astype(int)
        self.data['Week of occurrence'] = self.data['Week of occurrence'].astype(int)
#        self.data.columns=['Week of occurrence','Health Board','Location of death','Cause of Death','deaths']
#        #self.data.dropna() #drop any columns with null values
#        validweeks=[n for n in self.data['Week of occurrence'].unique() if valid_int(n)] #only week numbers that are valid
#        print(len(self.data.index))
#        self.data=self.data[self.data['Week of occurrence'].isin(validweeks)] #select rows only with valid week numbers
#        print(len(self.data.index))
        
        
    def weeks(self):
        return sorted([int(z) for z in self.data['Week of occurrence'].unique()])
        
    def districts(self):
        return sorted([z for z in self.data['Health Board'].unique()])

    def parse(self):
        for district in self.districts():
            for week in self.weeks():
                self.parse_week(week,district)
        if self.edition:
            configs.userconfig.update('Scotland','latest_deaths',self.edition)
#        if self.edition:
#            configs.userconfig.update('ONS','latest_update',self.edition)
    def parse_week(self,week,district,_update=True):
        week_str=str(week)
        sub=self.data[(self.data['Health Board']==district)&(self.data['Week of occurrence']==week)]
        _allc19=sub[(sub['Cause of Death']=='COVID-19')]['Deaths'].sum()
        _all=sub['Deaths'].sum()
        careh=sub[(sub['Location of death']=='Care Home')]['Deaths'].sum()
        careh19=sub[(sub['Cause of Death']=='COVID-19')&(sub['Location of death']=='Care Home')]['Deaths'].sum()
        hosp19=sub[(sub['Cause of Death']=='COVID-19')&(sub['Location of death']=='Hospital')]['Deaths'].sum()
        print(f'District: {district} Week: {week} C19:{_allc19} All: {_all} Carehomes {careh} ({careh19} C19)')
        qrow=CovidWeek.objects.filter(date=sunday(week),areaname=district)
        if qrow:
            row=qrow[0]
            #print(row)
            if _update:
                update_row(row,_all,_allc19,careh,careh19,hosp19)
        else:
            if _update:
                areacode=scotcode[district]
                _nation='Scotland'
                row=CovidWeek(date=sunday(week),areacode=areacode,nation=_nation,areaname=district,week=week)
                print(f'Created week {sunday(week)} for {district}')
                row.save()
                update_row(row,_all,_allc19,careh,careh19,hosp19)
                
    def update_cum_deaths(self):
        for d in scotcode.values():
            update_cum_district_death(d)

class Scot_Average(Scot_Importer):
    
    def process(self,f):
        self.open_csv(f)
        self.fix()
        
    def open_csv(self,f):
        self.data=pandas.read_csv(f, encoding= "iso-8859-1",skiprows=2)
    
    def fix(self):
        self.data=self.data[self.data.columns[:5]].dropna()
        validweeks=self.weeks()
        self.data=self.data[self.data['week of occurrence'].isin(validweeks)]
        
        self.data['year']=self.data['year'].astype(int)
        self.data['week of occurrence']=self.data['week of occurrence'].astype(int)
    
    def weeks(self):
        return [n for n in self.data['week of occurrence'].unique() if valid_int(n)]
    
    def parse(self):
        for place in self.districts():
            for week in self.weeks():
                self.parserow(place,week)
    
    def districts(self):
        return sorted([z for z in self.data['health board'].unique()])

    
    def parserow(self,place,week):
        areacode=scotcode[place]
        try:
            sub=self.data[(self.data['week of occurrence']==week)&(self.data['health board']==place)]
            wk, created = AverageWeek.objects.get_or_create(
            week=week,
            areacode=areacode
            )
            location=place
            print(f'Parsing: Area: {place} week {week}')
            wk.weeklyalldeaths=sub['number of deaths'].sum()/5
            wk.weeklyhospitaldeaths=sub[(sub['location']=='Hospital')]['number of deaths'].sum()/5
            wk.weeklyelsewheredeaths=None
            wk.weeklyhospicedeaths=None
            wk.weeklyothercommunaldeaths=sub[(sub['location']=='Other institution')]['number of deaths'].sum()/5
            wk.weeklycarehomedeaths=sub[(sub['location']=='Care Home')]['number of deaths'].sum()/5
            wk.weeklyhomedeaths=sub[(sub['location']=='Home / Non-institution')]['number of deaths'].sum()/5
            wk.save()
            print(wk.__dict__)
        except Exception as e:
            print(e)
    
    
class Scot_Cases(Scot_Importer):
    def process(self,f=CASES_URL,live=True):
        if live:
            self.fetch_csv(f)
        else:
            self.open_csv(path)
        self.fix()
        
        if self.update_check():
            self.ingest_all()
        
    def update_check(self):
        self.edition=self.data.index.max()
        print(f'Latest Scot cases data: {self.edition}')
        scotupdate=configs.config.get('Scotland')
        if scotupdate:
            self.last_update=scotupdate.get('latest_cases')
            print(f'Previously stored Scot cases data:{self.last_update}')
        else:
            self.last_update=None
            return True
        if self.last_update != str(self.edition):
            print('Update Scottish cases')
            return True
        else:
            print('Scottish cases up to date')
            return False
        
    def fetch_csv(self,url=CASES_URL):
        path=os.path.join(DATA_STORE,'Scotland_latestcases.csv')
        res=requests.get(url)
        with open(path, 'wb') as f:
            f.write(res.content)
        self.open_csv(path)
    
    def open_csv(self,path):
        self.data = pandas.read_csv(path, skiprows=7, encoding= "utf-8") #skip the first rows

    def districts(self):
        return scotcode.keys()


    def fix(self):
        zt=self.data[self.data.columns[1:]].T #drop first column and transpose
        labels=[n for n in zt.iloc[0]] #grab column labels from first row
        zt.columns=labels
        self.data=zt[1:]
        self.data.index=pandas.to_datetime(self.data.index)
        
    def ingest_all(self):
        """pull all daily cases from all Scottish areas"""
        for sequence in self.districts():
            self.sequence_ingest(sequence)
        if self.edition:
            configs.userconfig.update('Scotland','latest_cases',str(self.edition))
        
    def sequence_ingest(self,place):
        """ingest cases for region"""
        data=self.data
        counter=0
        for day in self.data.index:
            
            yesterday=self.data[self.data.index==day-timedelta(1)][place].fillna(0)
            if yesterday.empty:
                yesterday=0
            elif yesterday.item()=="*":
                yesterday=0
            else:
                yesterday=int(yesterday)
            totalcases=self.data[self.data.index==day][place].fillna(0).item()
            if totalcases=="*":
                totalcases=0
            else:
                totalcases=int(totalcases)
            if totalcases:
                today=totalcases-yesterday
            else:
                today=0
            
            print(f'Place:{place} Date: {day:%d/%m} Yesterday:{yesterday} Today:{today} Total:{totalcases}')
            #datestring=item['specimenDate']
            date=day
            areacode=scotcode[place]
            row,created=DailyCases.objects.get_or_create(specimenDate=timeaware(date),areacode=areacode)
            row.areaname=place
            row.dailyLabConfirmedCases=today
            row.totalLabConfirmedCases=totalcases
            row.changeInDailyCases=None #item['changeInDailyCases']
            row.dailyTotalLabConfirmedCasesRate=None #item['dailyTotalLabConfirmedCasesRate']
            row.previouslyReportedDailyCases=None #item['previouslyReportedDailyCases']
            row.previouslyReportedTotalCases=None #item['previouslyReportedTotalCases']
            row.changeInTotalCases=None #item['changeInTotalCases']
            row.save()
            counter+=1
        print(f'Processed: {counter} rows')
        update_weekly_total(areacode=scotcode[place],areaname=place)


def valid_int(s):
    try:
        n=int(s)
        return n
    except:
        return None
    
 