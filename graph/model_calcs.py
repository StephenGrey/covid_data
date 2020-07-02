from .models import CovidWeek
import datetime,json
one_week=datetime.timedelta(7)

def calc_new_cases():
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
	
def districts():
	q=CovidWeek.objects.values('areacode').distinct()
	
	return [d['areacode'] for d in q]

def district_names():
	q=CovidWeek.objects.values('areaname').distinct()
	return [d['areaname'] for d in q]

def nations():
	q=CovidWeek.objects.values('nation').distinct()
	return [d['nation'] for d in q]
	
def query_by_nation(nation):
	return CovidWeek.objects.filter(nation=nation)
	
	
def output_all():
	all_data={}
	for nation in nations():
		q=query_by_nation(nation)
		nationset={}
		for place in district_names():
			district=q.filter(areaname=place,date__range=["2020-02-14", "2020-06-12"])	
			#print(district)
			totalcumdeaths=[i.totcumdeaths for i in district]
			weeklydeaths=[i.weeklydeaths for i in district]
			weeklycases=[i.weeklycases for i in district]
			estcasesweekly=[i.estcasesweekly for i in district]
			dataset={ 
				1:{'label':"Estimate- new infections ",'data':estcasesweekly},
				2:{'label':'Total Deaths','data':totalcumdeaths},
				3:{'label':'Covid-Positive Tests','data':weeklycases},
				4:{'label':"Weekly deaths",'data':weeklydeaths},
				'placename':place
				}
			nationset[place]=dataset
		all_data[nation]=nationset
	return all_data
	
	
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
			
			