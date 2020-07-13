import os,json,requests
from .models import DailyCases,CovidWeek
from datetime import datetime,timedelta
import pytz
from . import ons_week, model_calcs



URL="https://c19downloads.azureedge.net/downloads/json/coronavirus-cases_latest.json"
TIMEOUT=60
DATALOAD={}
AREACODE="E08000025"
AREA="Birmingham"

class NoContent(Exception):
    pass

class NoEntry(Exception):
    pass

class Fetch_PHE():
	def __init__(self):
		self.fetch()    

	def fetch(self,url=URL):
		""" get the latest cases data"""
		self.data=lookup_json(url)

	def sequence_ingest(self,sequence):
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

def update_weekly_cases():
    q=CovidWeek.objects.filter(nation='England')
    for place in q.values('areacode','areaname').distinct():
        areacode=place['areacode']
        area=place['areaname']
        if areacode and area:
            update_weekly_total(areacode=areacode,areaname=area)

def update_weekly_total(areacode=AREACODE,areaname=AREA):
    start,stop=model_calcs.RANGE_WEEK
    print(f'Processing {areaname}')
    for week in range(start,stop+1):
        end_day=ons_week.week(week)+timedelta(2) #FIX : DEATH RATES ARE CALCULATED TO TWO DAYS EARLIER
        week_total=weekly_total(end_day,areacode=areacode,areaname=areaname)
        print(f'{areaname}: Weektotal for week number {week} ending {end_day}: {week_total}')
        
        if week_total is not None:
            try:
                stored,created=CovidWeek.objects.get_or_create(areacode=areacode,date=end_day)
                #print(stored.weeklycases)
                if stored.weeklycases != week_total:
                    print(f'{areaname}: updating week {week} from {stored.weeklycases} to {week_total}')
                    stored.weeklycases=week_total
                    stored.areaname=areaname
                    stored.save()
                if created:
                    stored.nation=ons_week.nation[areacode]
                    stored.save()
                    #should add nation here when creating new entry
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
                



#DATALOAD=main()

def process(data):
	data=main(eg)
	latest=data['ltlas']#list of latest entries - lower teir
	latest_upper_tier=data['utlas'] # upper tier
	metadata=data['metadata']
	daily_countrylevel=data['countries'] #just England
	regions=data['regions'] #English regions
	bigtotal=['dailyRecords']


def name_index():
	q=DailyCases.objects.values('areacode','areaname').distinct()
	_i={}
	for place in q:
		areacode=place['areacode']
		area=place['areaname']
		_i[areacode]=area
	return _i




	
#{'areaCode': 'E09000033', 'areaName': 'Westminster', 'specimenDate': '2020-07-09', 'dailyLabConfirmedCases': 0, 'previouslyReportedDailyCases': None, 'changeInDailyCases': None, 'totalLabConfirmedCases': 773, 'previouslyReportedTotalCases': None, 'changeInTotalCases': None, 'dailyTotalLabConfirmedCasesRate': 302.8}

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
        print(datestring)
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






