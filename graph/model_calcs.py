from .models import CovidWeek,AverageWeek,CovidScores,DailyCases
from django.db.models import Sum
import datetime,json,os,logging,pandas as pd
one_week=datetime.timedelta(7)
from . import ons_week
from utils import time_utils
import configs
from configs import userconfig
log = logging.getLogger('api.graph.model_calcs')
RANGE=["2020-02-07", "2020-11-28"]
RANGE_WEEK=[6, 48]
DELAY=datetime.timedelta(4)  #delay before most cases are published i.e. case rate becomes accurate
DATA_STORE=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../data'))

MAP_PATH='graph/json/UK_corrected_topo.json'

DELAY_FILE=os.path.join(DATA_STORE,'Last7Delays.json')
try:
    with open(DELAY_FILE,'r') as json_file:
        DELAYS=json.loads(json_file.read())
except Exception as e:
    DELAYS={}
    log.error(e)
    log.info('Cannot load 7-day delays data')
    

#MOVING TO USING ONLY WEEK NUMBERS - TO AVOID DISCREPANCY SCOT AND E+W ON WEEK ENDING

def excess_deaths_district(place='Birmingham',save=False):
	"""calculate rate of excess death for one district; for weeks when 2020 data existss"""
	district=CovidWeek.objects.filter(areaname=place,week__range=RANGE_WEEK).order_by('week')
	areacode=district[0].areacode

	all_deaths_2020=0
	all_carehome_deaths_2020=0
	count=0 #count the number of weeks with data
	for i in district:
		if i.weeklyalldeaths is None: #check for when data runs out
			break
		all_deaths_2020+=i.weeklyalldeaths
		if i.weeklycarehomedeaths is not None:
			all_carehome_deaths_2020+=i.weeklycarehomedeaths
		count+=1
	
	#gather the dates for same weeks
	averages=AverageWeek.objects.filter(areacode=areacode,week__range=[RANGE_WEEK[0],RANGE_WEEK[0]+count-1])	
	
	if averages:
		_data=True
		average_deaths=sum([i.weeklyalldeaths for i in averages])
		
		try:
			average_carehome_deaths=sum([i.weeklycarehomedeaths for i in averages])
		except:
			average_carehome_deaths=None
		excess=int(all_deaths_2020-average_deaths)
		
		try:
			excess_carehomes=int(all_carehome_deaths_2020-average_carehome_deaths)
		except:
			excess_carehomes=None
		log.debug(f'Excess deaths in {place}: {excess} (care homes: {excess_carehomes})')
	else:
		_data=False
		log.error(f'No average data for {place}')
	if save:
		av, created = CovidScores.objects.get_or_create(
			areaname=place,
			)
		if _data:
			av.excess_deaths=excess
			av.excess_deaths_carehomes=excess_carehomes
			av.save()
		else:
			av.excess_deaths=None
			av.excess_deaths_carehomes=None
			av.save()

def excess_deaths():
	"parse through all districts in database , updating the excess death calc"""
	for place in district_names():
		excess_deaths_district(place=place,save=True)

def update_cum_deaths():
	"""parse through all districts in database , updating the cumulative death total"""
	log.info('Updating cumulative death total')
	for d in districts():
		update_cum_district_death(d)

def update_cum_district_death(d):		
	"""update cumulative death total in one district"""
	if True:
		cum=0
		
		for w in CovidWeek.objects.filter(areacode=d).order_by('week'):
			if w.weeklydeaths is not None:
				cum+=w.weeklydeaths	
				if cum != w.totcumdeaths:
					log.debug(f'District {d} stored: {w.totcumdeaths} calc {cum}')
					w.totcumdeaths=cum
					w.save()
			else:
				w.totcumdeaths=None
				w.save()
		
def calc_excess_rates():
	"""update all the excess death rates for all districts"""
	for place in district_names():
		i=CovidScores.objects.get(areaname=place)
		if i.population and i.excess_deaths is not None:
			rate=round(i.excess_deaths/i.population*100000,1)
			#print(rate)
			i.excess_death_rate=rate
			i.save()
		else:
			log.info(f'Data missing for {place}')

def calc_newcases_rates():
	"""update all the new cases rates for all districts"""
	log.info('Beginning calc of new cases rates')
	_delay=DELAY
	_latest_update=latest_update()
	_today=datetime.date.today()
	_range=[_latest_update-one_week-_delay,_latest_update-_delay]
	_cases_end=f"{_latest_update-_delay:%a %d %b}"
	_14range=[_latest_update-one_week-_delay-datetime.timedelta(14),_latest_update-_delay-datetime.timedelta(14)]
	rates={}	
	for place in district_names():
		i=CovidScores.objects.get(areaname=place)
		total_cases=DailyCases.objects.filter(specimenDate__range=_range,areaname=place).aggregate(Sum('dailyLabConfirmedCases'))['dailyLabConfirmedCases__sum']
		total_cases14=DailyCases.objects.filter(specimenDate__range=_14range,areaname=place).aggregate(Sum('dailyLabConfirmedCases'))['dailyLabConfirmedCases__sum']
		try:
			change=round(((total_cases-total_cases14)/total_cases14)*100,1)
		except:
			change=None
		newcases_rate=round(total_cases/i.population*100000,1) if total_cases is not None and i.population else None
		rates[place]=newcases_rate
		i.latest_case_rate=newcases_rate
		i.change_case_rate=change
		log.debug(f'Place: {place} Cases: {total_cases} 14DayAgo: {total_cases14} Rate:{newcases_rate} change:{change}%')
		i.save()
	log.info('Completed newcase rate calculations')
		#print([(k, v) for k, v in sorted(rates.items(), key=lambda item: item[1]) if v])
#i=CovidScores.objects.get(areaname=place)
#		if i.population and i.excess_deaths:
#			rate=round(i.excess_deaths/i.population*100000,1)
#			i.excess_death_rate=rate
#			i.save()
#		else:
#			print(f'Data missing for {place}')

def calc_new_cases():
	"""calculate the new cases from cumulative cases"""
	for d in districts():
		for w in CovidWeek.objects.filter(areacode=d):
			lastweek=CovidWeek.objects.filter(areacode=d,week=w.week-1)
			if lastweek:
				lasttotal=lastweek[0].totcumcases
			else:
				lasttotal=0
			newcases=w.totcumcases-lasttotal
			#print(f'Date: {w.date} CumCases: {w.totcumcases} NewCases: {newcases}')
			w.weeklycases=newcases
			w.save()
		
	return 


def local_cases_range(start_date='2020-06-01',end_date='2020-07-01',areaname='Hartlepool'):
	"""calculate new cases in a time range"""
	try:
		q=DailyCases.objects.filter(areaname=areaname,specimenDate=start_date)[0]
		start_total=q.totalLabConfirmedCases
	
		q=DailyCases.objects.filter(areaname=areaname,specimenDate=end_date)[0]
		end_total=q.totalLabConfirmedCases
		return end_total-start_total
		
	except Exception as e:
		log.info(e)
		return None
	

def cases_range(start_date='2020-06-01',end_date='2020-07-01'):
	"""calculate new cases in a time range across all areas"""
	for place in ons_week.stored_names.values():
		diff=local_cases_range(start_date=start_date,end_date=end_date,areaname=place)
		print(f"{place},{diff}")
		
def fix_names():
    _i=ons_week.stored_names
    for missing in CovidWeek.objects.filter(areaname='Hartlepool'):
        try:
            log.info(f'Areacode {missing.areacode} is {_i[missing.areacode]}')
            missing.areaname=_i[missing.areacode]
            missing.save()
        except Exception as e:
            print(e)
	
def districts():
	q=CovidWeek.objects.values('areacode').distinct()
	
	return [d['areacode'] for d in q]

def district_names():
	q=CovidWeek.objects.values('areaname').distinct()
	return [d['areaname'] for d in q]

def nations():
	q=CovidWeek.objects.values('nation').distinct()
	return [d['nation'] for d in q]
	
def nations_index():
	nations={}
	for district in CovidWeek.objects.values('areacode','nation').distinct():
		nations[district['areacode']]=district['nation']
	return nations
	
def query_by_nation(nation):
	return CovidWeek.objects.filter(nation=nation)
	
def output_district(place,q=None):
	"""
	Output series of data for a place >>> to be served to chart
	
	"""
	if q:
		district=q.filter(areaname=place,week__range=RANGE_WEEK).order_by('week')
	else:
		district=CovidWeek.objects.filter(areaname=place,week__range=RANGE_WEEK).order_by('week')
	
	
	log.debug(district)
	
	if district:
		#print([f"{i.date:%d/%m}" for i in district])
		totalcumdeaths=[i.totcumdeaths for i in district]
		#print(totalcumdeaths)
		weeklydeaths=[i.weeklydeaths for i in district]
		weeklycases=[i.weeklycases for i in district]
		estcasesweekly=[i.estcasesweekly for i in district]
		
		weeklyalldeaths=[i.weeklyalldeaths for i in district]
		weeklycarehomedeaths=[i.weeklycarehomedeaths for i in district]

		areacode=district[0].areacode

		averages=AverageWeek.objects.filter(areacode=areacode,week__range=RANGE_WEEK)
		totavdeaths=[str(i.weeklyalldeaths) for i in averages]
		avcaredeaths=[str(i.weeklycarehomedeaths) for i in averages]
		#print(place)
		#print(weeklycases)
		sc=CovidScores.objects.get(areaname=place)
		if sc:
			excess=sc.excess_deaths
			excess_ch=sc.excess_deaths_carehomes
			excess_rate=sc.excess_death_rate
			
			if not excess or not excess_ch or not excess_rate:
				excess,excess_ch,excess_rate="N/A","N/A","N/A"
			
		else:
			excess,excess_ch,excess_rate="N/A","N/A","N/A"
		
		last=DailyCases.objects.filter(areaname=place).order_by('-specimenDate')[:50][::-1]
		last_cases=[i.dailyLabConfirmedCases for i in last]
		last_cases_rolling=rolling_averages(last_cases)
		last_dates=[f"{i.specimenDate:%d-%b}" for i in last]
		week_date_labels=['Feb 7','Feb 14','Feb 21', 'Feb 28','Mar 6','Mar 13','Mar 20', 'Mar 27','Apr 3','Apr 10', 'Apr 17','Apr 24','May 1','May 8','May 15','May 22','May 29','June 5', 'June 12','June 19','June 26','Jul 3','Jul 10', 'Jul 17', 'Jul 24','Jul 31','Aug 7','Aug 14','Aug 21','Aug 28','Sep 4','Sep 11','Sep 18','Sep 25','Oct 2','Oct 9','Oct 16','Oct 23','Oct 30','Nov 6','Nov 13','Nov 20','Nov 27']
		last_deaths=[i.deaths for i in last]
		last_deaths_rolling=rolling_averages(last_deaths)
		last_pubdeaths=[i.published_deaths for i in last]
		dataset={ 
			1:{'label':"Weekly new infections -Reuters estimate",'data':estcasesweekly},
			2:{'label':'Total Deaths','data':totalcumdeaths},
			3:{'label':'Weekly Covid-Positive Tests','data':weeklycases},
			4:{'label':"Weekly Covid19 deaths",'data':weeklydeaths},
			
			5:{'label':"All-Causes deaths",'data':weeklyalldeaths},
#					4:{'label':"Hospital deaths",'data':weeklyhospitaldeaths},
			6:{'label':"All carehome deaths",'data':weeklycarehomedeaths},
			7:{'label':"5Y average total deaths",'data':totavdeaths},
			8:{'label':"5Y average carehome deaths",'data':avcaredeaths},
			9:{'label':"Covid19 new cases",'data':last_cases,'labelset':last_dates},
			10:{'label':"Covid19 deaths",'data':last_deaths,'labelset':last_dates},
			11:{'label':"Covid19 deaths published",'data':last_pubdeaths,'labelset':last_dates},
			12:{'label':"Covid19 new cases (rolling 7-day average)",'data':last_cases_rolling,'labelset':last_dates},
			13:{'label':"Covid19 new deaths(rolling 7-day average)",'data':last_deaths_rolling,'labelset':last_dates},

			'week_date_labels':week_date_labels,
			'caseslabel':f'Cases in {place} in last 50 days',
			'deathslabel':f'Covid deaths in {place} in last 50 days',
			'excess':f"Excess deaths in {place}: {excess} ({excess_rate} per 100k) including {excess_ch} in care homes)",
			'placename':place, 'infectlabel':f"Real estimated infections in {place} vs Covid+ tests"
			}
	else:
		dataset={}
	#print(dataset)
	return dataset
	
	
def output_all():
	all_data={}
	for nation in nations():
		print(nation)
		q=query_by_nation(nation)
		nationset={}
		for place in district_names():
			nationset[place]=output_district(place,q=None)	
		all_data[nation]=nationset
	return all_data


def output_rates(subset=None,exclude=None):
	"""output rates into an array """
	data=[]
	
	if exclude and subset:
		q=CovidScores.objects.exclude(areaname__in=exclude)
		q=q.filter(areaname__in=subset)
	elif exclude:
		q=CovidScores.objects.exclude(areaname__in=exclude)
	elif subset:
		q=CovidScores.objects.filter(areaname__in=subset)
	else:
		q=CovidScores.objects.all()
		
	for score in q:
		excess=round(float(score.excess_death_rate)) if score.excess_death_rate is not None else None
		cases_rate=round(float(score.latest_case_rate)) if score.latest_case_rate is not None else None
		change_case_rate=round(float(score.change_case_rate)) if score.change_case_rate is not None else None
		data.append({
    "areaname": score.areaname,
    "wave2":score.wave2_PHEdeaths,
    "wave2_rate":score.wave2_deathrate,
    "last30":score.last_month_PHEdeaths,
    "excess": excess,
    "cases_rate":cases_rate,
    "cases_change":change_case_rate,
    "delays":DELAYS.get(score.areaname),
    	})
	return data


def save_all_rates(filename):
	"""dump all Covid19 rates to Json"""
	data=output_rates()
	with open(filename, 'w') as outfile:
		json.dump(data, outfile)


def district_deaths(place='Birmingham'):
	district=CovidWeek.objects.filter(areaname=place,week__range=RANGE_WEEK)
	areacode=district[0].areacode
	print(areacode)	
	totalcumdeaths=[i.totcumdeaths for i in district]
	weeklydeaths=[i.weeklydeaths for i in district]
	weeklyalldeaths=[i.weeklyalldeaths for i in district]
	weeklyhospitaldeaths=[i.weeklyhospitaldeaths for i in district]
	weeklycarehomedeaths=[i.weeklycarehomedeaths for i in district]
	
	averages=AverageWeek.objects.filter(areacode=areacode,week__range=RANGE_WEEK)
	totavdeaths=[str(i.weeklyalldeaths) for i in averages]
	avcaredeaths=[str(i.weeklycarehomedeaths) for i in averages]
	
	dataset={ 
				1:{'label':'Total Deaths','data':totalcumdeaths},
				2:{'label':"COVID-19 deaths",'data':weeklydeaths},
				3:{'label':"All-Causes deaths",'data':weeklyalldeaths},
#				4:{'label':"Hospital deaths",'data':weeklyhospitaldeaths},
				4:{'label':"Care home deaths",'data':weeklycarehomedeaths},
				5:{'label':"Average total deaths",'data':totavdeaths},
				6:{'label':"Av care home deaths",'data':avcaredeaths},
				'placecode':place
				}
	return dataset

def district_deaths_json(place='Birmingham'):
	data=district_deaths(place=place)
	
	return json.dumps(data)
	
def json_all():
    
    data=output_all()
    return json.dumps(data)

def save_all(filename):
	data=output_all()
	with open(filename, 'w') as outfile:
		json.dump(data, outfile)

nat_index={"England":"1", "Wales":"2", "Scotland":"3",  "Northern Ireland":"4"}

def output_tags():
	for nation in nations():
		tag=nat_index[nation]
		q=query_by_nation(nation)
		for item in q.values('areaname').distinct().order_by('areaname'):
			placename=item['areaname']
			print(f"""<option value="{placename}" data-tag="{tag} ">{placename}</option>""")
			

def rolling_averages(series,period=7, cutoff=4):
	df = pd.DataFrame({'cases':series[:-cutoff]})
	df['rolling'] = df['cases'].rolling(period).mean()
	new_series=df.round(decimals=1).where(pd.notnull(df), None)['rolling'].tolist()
	return new_series+[None for x in range(cutoff)]

def get_rate(item,key='cases_rate'):
	if not item[key]:
		return 0
	return item[key]
	
def top_rate(ratelist, key='cases_rate',n=10,_reverse=True):
	return sorted(ratelist,key=lambda x: get_rate(x,key=key),reverse=_reverse)[:n]
			
def sort_rate(ratelist,key='cases_rate',_reverse=True):
	return sorted(ratelist,key=lambda x: get_rate(x,key=key),reverse=_reverse)
		
		
def latest_update():
	PHEstored=configs.config.get('PHE')
	edition=PHEstored.get('latest_update')
	lastupdate=time_utils.parseISO(edition).date()
	return lastupdate
#	lastupdate_str=f'{lastupdate: %a %d %b}'



		
	