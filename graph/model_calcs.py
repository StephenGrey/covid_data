from .models import CovidWeek,AverageWeek,CovidScores
import datetime,json
one_week=datetime.timedelta(7)
from . import ons_week

RANGE=["2020-02-14", "2020-07-05"]
RANGE_WEEK=[7, 27]

def excess_deaths_district(place='Birmingham',save=False):
	
	district=CovidWeek.objects.filter(areaname=place,date__range=RANGE)
	areacode=district[0].areacode

	all_deaths_2020=sum([i.weeklyalldeaths for i in district])
	all_carehome_deaths_2020=sum([i.weeklycarehomedeaths for i in district])
	
	averages=AverageWeek.objects.filter(areacode=areacode,week__range=RANGE_WEEK)	
	
	if averages:
		_data=True
		average_deaths=sum([i.weeklyalldeaths for i in averages])
		average_carehome_deaths=sum([i.weeklycarehomedeaths for i in averages])
	
		excess=int(all_deaths_2020-average_deaths)
		excess_carehomes=int(all_carehome_deaths_2020-average_carehome_deaths)
		print(f'Excess deaths in {place}: {excess} (care homes: {excess_carehomes})')
	else:
		_data=False
		print(f'No average data for {place}')
	if save:
		av, created = CovidScores.objects.get_or_create(
			areaname=place,
			)
		if _data:
			av.excess_deaths=excess
			av.excess_deaths_carehomes=excess_carehomes
			av.save()
			print(av.__dict__)
		else:
			av.excess_deaths=None
			av.excess_deaths_carehomes=None
			av.save()

def excess_deaths():
	for place in district_names():
		excess_deaths_district(place=place,save=True)


def update_cum_deaths():
	for d in districts():
		cum=0
		print(d)
		for w in CovidWeek.objects.filter(areacode=d):
			if w.weeklydeaths:
				cum+=w.weeklydeaths
				if cum != w.totcumdeaths:
					print(f'stored: {w.totcumdeaths} calc {cum}')
					w.totcumdeaths=cum
					w.save()
		
		
def calc_excess_rates():
	for place in district_names():
		i=CovidScores.objects.get(areaname=place)
		if i.population and i.excess_deaths:
			rate=round(i.excess_deaths/i.population*100000,1)
			i.excess_death_rate=rate
			i.save()

def calc_new_cases():
	"""calculate the new cases from cumulative cases"""
	for d in districts():
		for w in CovidWeek.objects.filter(areacode=d):
			lastweek=CovidWeek.objects.filter(areacode=d,date=w.date-one_week)
			if lastweek:
				lasttotal=lastweek[0].totcumcases
			else:
				lasttotal=0
			newcases=w.totcumcases-lasttotal
			#print(f'Date: {w.date} CumCases: {w.totcumcases} NewCases: {newcases}')
			w.weeklycases=newcases
			w.save()
		
	return 

def fix_names():
    _i=ons_week.stored_names
    for missing in CovidWeek.objects.filter(areaname='Hartlepool'):
        try:
            print(f'Areacode {missing.areacode} is {_i[missing.areacode]}')
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
	if q:
		district=q.filter(areaname=place,date__range=RANGE)
	else:
		district=CovidWeek.objects.filter(areaname=place,date__range=RANGE)
	
	if district:
		totalcumdeaths=[i.totcumdeaths for i in district]
		weeklydeaths=[i.weeklydeaths for i in district]
		weeklycases=[i.weeklycases for i in district]
		estcasesweekly=[i.estcasesweekly for i in district]
		
		weeklyalldeaths=[i.weeklyalldeaths for i in district]
		weeklycarehomedeaths=[i.weeklycarehomedeaths for i in district]

		areacode=district[0].areacode

		averages=AverageWeek.objects.filter(areacode=areacode,week__range=RANGE_WEEK)
		totavdeaths=[str(i.weeklyalldeaths) for i in averages]
		avcaredeaths=[str(i.weeklycarehomedeaths) for i in averages]
		
		print(place)
		print(weeklycases)
		sc=CovidScores.objects.get(areaname=place)
		if sc:
			excess=sc.excess_deaths
			excess_ch=sc.excess_deaths_carehomes
			excess_rate=sc.excess_death_rate
			
			if not excess or not excess_ch or not excess_rate:
				excess,excess_ch,excess_rate="N/A","N/A","N/A"
			
		else:
			excess,excess_ch,excess_rate="N/A","N/A","N/A"
			
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
			'excess':f"Excess deaths: {excess} ({excess_rate} per 100k) including {excess_ch} in care homes)",
			'placename':place,
			}
	else:
		dataset={}
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

def district_deaths(place='Birmingham'):
	district=CovidWeek.objects.filter(areaname=place,date__range=RANGE)
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
			

def add_averages():
	for wk in AverageWeek.objects.all():
			_sum=wk.weeklyhospitaldeaths+wk.weeklyelsewheredeaths+wk.weeklyhospicedeaths+wk.weeklyothercommunaldeaths+wk.weeklycarehomedeaths+wk.weeklyhomedeaths
			wk.weeklyalldeaths=_sum
			wk.save()
