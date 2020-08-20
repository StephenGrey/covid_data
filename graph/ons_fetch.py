import requests,json,csv
from .ons_week import week as ons_week,sunday,stored_names,nation,weeks
from .models import CovidWeek,CovidScores
from .import_csv import URLImporter,PandaImporter
import configs
from configs import userconfig
from datetime import date,timedelta
#WEEKLY_DEATHS_FILTER=configs.config['ONS']['weekly_deaths_filter'] #get base path of the docstore
#print(WEEKLY_DEATHS_FILTER)

ID="weekly-deaths-local-authority"
MASTER_URL="https://api.beta.ons.gov.uk/v1/datasets"

POST_URL= "https://api.beta.ons.gov.uk/v1/filters"
#OUTPUT_URL="https://api.beta.ons.gov.uk/v1/filter-outputs/"

"""
mismatch: Isles of Scilly & Cornwall and Isles of Scilly


"""

TIMEOUT=20

EG={
    "dataset": {
        "id": "weekly-deaths-local-authority",
        "edition": "time-series",
        "version": 12
    },
    "dimensions": [
        {
            "name": "registrationoroccurrence",
            "options": [
                "occurrences"
                       ]
        }
                  ]
}

class ConnectionError(Exception):
    pass

class ONS_Importer(PandaImporter):
        #['v4_0', 'calendar-years', 'time', 'admin-geography', 'geography', 'week-number', 'week', 'cause-of-death', 'causeofdeath', 'place-of-death', 'placeofdeath', 'registration-or-occurrence', 'registrationoroccurrence']
    
    def weeks(self):
        return sorted([int(z[5:]) for z in self.data['week-number'].unique()])
        
    def districts(self):
        return sorted([z for z in self.data['admin-geography'].unique()])
    
    def download(self):
        print(f'downloading {self.download_url}')
        if self.download_url:
            self.fetch(self.download_url)
            
    
    def process(self):
        _id,url=self.get_download_link()
        last_update=configs.config['ONS'].get('latest_update')
        print(f"Latest edition: {_id}   Most recent update {last_update}")
        if last_update != _id:
            self.download()
            self.parse()
            return True
        else:
            return False
            
    def parse(self):
        for district in self.districts():
            for week in self.weeks():
                week_data={}
                self.parse_week(week,district)
        if self.edition:
            configs.userconfig.update('ONS','latest_update',self.edition)

    def parse_week(self,week,district,_update=True):
        week_str=f"week-{week}"
        year="2020"
        sub=self.data[(self.data['admin-geography']==district)&(self.data['registrationoroccurrence']=='Occurrences')&(self.data['week-number']==week_str)]
        _allc19=sub[(sub['causeofdeath']=='COVID 19')]['v4_0'].sum()
        _all=sub[(sub['causeofdeath']=='All causes')]['v4_0'].sum()
        careh=sub[(sub['causeofdeath']=='All causes')&(sub['placeofdeath']=='Care home')]['v4_0'].sum()
        careh19=sub[(sub['causeofdeath']=='COVID 19')&(sub['placeofdeath']=='Care home')]['v4_0'].sum()
        hosp19=sub[(sub['causeofdeath']=='COVID 19')&(sub['placeofdeath']=='Hospital')]['v4_0'].sum()
        print(f'District: {district} Week: {week} C19:{_allc19} All: {_all}')
        qrow=CovidWeek.objects.filter(week=week,areacode=district)
        if qrow:
            row=qrow[0]
            #print(row)
            if _update:
                update_row(row,_all,_allc19,careh,careh19,hosp19)
        else:
            if _update:
                areaname=stored_names[district]
                _nation=nation[district]
                row=CovidWeek(areacode=district,nation=_nation,areaname=areaname,week=week)
                print(f'Created week {sunday(week)} for {district}')
                row.save()
                update_row(row,_all,_allc19,careh,careh19,hosp19)

    def get_download_link(self):
        latest=get_latest()
        url=latest.get('href')
        _id=latest.get('id')
        if url and _id:
            self.edition=_id
            
            configs.userconfig.update('ONS','latest_edition',self.edition)
            
            print(f'Latest edition {_id}: {url}')
            resp=lookup_json(url)
            try:
                downloads=resp['downloads']['csv']['href']
                self.download_url=downloads
                configs.userconfig.update('ONS','latest_download',url)
                return _id,downloads
            except Exception as e:
                print(e)
                return None,None        
        else:
            return None,None

    
    def update_filter(self):
        resp=post_api(url=POST_URL+'?submitted=true',params=EG)
        print(resp)
        FILTER_ID=resp['links']['filter_output']['id']
        print(f'Filter_id: {FILTER_ID}')        
        configs.userconfig.update('ONS','weekly_deaths_filter',FILTER_ID)

def update_row(row,_all,_allc19,careh,careh19,hosp19):
    _update=False
    
    print(f"stored weekly C19 deaths: {row.weeklydeaths}")
    if row.weeklydeaths !=_allc19:
        print(f'update total C19 deaths from {row.weeklydeaths} to {_allc19}')
        _update=True
        row.weeklydeaths=_allc19
        row.save()
    
    
    if row.weeklyC19hospitaldeaths !=hosp19:
        _update=True
        print(f'updating hospital C19 from {row.weeklycarehomedeaths} to {hosp19}')
        row.weeklyC19hospitaldeaths=hosp19
    
    
    if row.weeklycarehomedeaths !=careh:
        _update=True
        print(f'updating care home deaths from {row.weeklycarehomedeaths} to {careh}')
        row.weeklycarehomedeaths=careh
    
    
    if row.weeklyC19carehomedeaths !=careh19:
        _update=True
        print(f'updating care home C19 deaths from {row.weeklycarehomedeaths} to {careh19}')
        row.weeklyC19carehomedeaths=careh19
    
    
    if row.weeklyalldeaths !=_all:
        _update=True
        print(f'updating all deaths from {row.weeklyalldeaths} to {_all}')
        row.weeklyalldeaths=_all
    
    if _update:
        row.save()


class NoContent(Exception):
    pass

def weekly_deaths():
    """check the lastest COVID deaths by area"""
    latest=get_latest()
    latest_url=latest["href"]
    edition=latest["id"]
    print(f'latest_url:{latest_url} edition: {edition}')    
    options=get_all_options(latest_url=latest_url)
    #weeks_available=get_weeks_availalb
    #get_options(series=ID,dimension="geography",url="")
    #district_weeks(options=options)
    
    for place in options['geography']:
        district_week(geography=place,latest_url=latest_url,options=options)
    

def get_all_options(latest_url="",series=ID):
    
    fields=[i[0] for i in get_dimensions(url=latest_url)]
    print(f"Fields available {fields}")
    
    if not latest_url:
        latest_url=get_latest_url(_id=series)
    options={}
    for field in fields:
        o=get_options(dimension=field,url=latest_url)
        options[field]=o
    return options
    

def district_week(geography="E06000016",options="",latest_url="",series=ID):
    print(f"Fetching data for {geography}")
    if not latest_url:
        latest_url=get_latest_url(_id=series)
    if not options:
        options=get_all_options(latest_url=latest_url)
    reg_or_occ="occurrences"
    raw_weeks=[int(i[5:]) for i in options['week']]
    weeks=sorted(raw_weeks)
    data={}
    for week in weeks:
        print(f"Week: {week}")        
        
        week_data={}
        week_str=f"week-{week}"
        year="2020"
        try:
            for placeofdeath in options['placeofdeath']:
                url=f"{latest_url}/observations?geography={geography}&week={week_str}&time={year}&placeofdeath={placeofdeath}&causeofdeath=*&registrationoroccurrence={reg_or_occ}"
                content=lookup_json(url)
                for i in content['observations']:
                    field=f"{placeofdeath}_{i['dimensions']['causeofdeath']['id']}"
                    week_data[field]=int(i['observation'])
            week_data['all_covid']=week_data['home_covid-19']+week_data['care-home_covid-19']+week_data['elsewhere_covid-19']+week_data['hospital_covid-19']+week_data['other-communal-establishment_covid-19']+week_data['hospice_covid-19']
            #print(week_data['all_covid'])
            week_data['total_allcauses']=week_data['care-home_all-causes']+week_data['elsewhere_all-causes']+week_data['home_all-causes']+week_data['hospice_all-causes']+week_data['hospital_all-causes']+week_data['other-communal-establishment_all-causes']
            #print(week_data)
            qrow=CovidWeek.objects.filter(week=week,areacode=geography)
            row=next(iter(qrow), None)
            if row:
                _allc19=week_data['all_covid']
                hosp19=week_data['hospital_covid-19']
                careh=week_data['care-home_all-causes']
                careh19=week_data['care-home_covid-19']
                _all=week_data['total_allcauses']
                
                update_row(row,_all,_allc19,careh,careh19,hosp19)
                
            data[week]=week_data
        except Exception as e:
            print(e)
            print('week failed')
    

    return data

def correct_smallpops():
    cornwall=CovidScores.objects.get(areaname="Cornwall").population
    IoS=CovidScores.objects.get(areaname="Isles of Scilly").population
    
    CwIoS,created=CovidScores.objects.get_or_create(areaname="Cornwall and Isles of Scilly")
    CwIoS.population=cornwall+IoS
    CwIoS.save()
    print('Corrected Cornwall and Isles of Scilly pop')

    hack=CovidScores.objects.get(areaname="Hackney").population
    city=CovidScores.objects.get(areaname="City of London").population

    HaCi,created=CovidScores.objects.get_or_create(areaname="Hackney and City of London")
    HaCi.population=hack+city
    HaCi.save()
    print('Corrected Hackney and City of London pop')
    
def get_latest(_id=ID):
    """latest details of ONS series"""
    info=lookup_index(series=_id)[0]
    return info['links']['latest_version'] #.keys() #['latest_version']

def get_latest_url(_id=ID):
    """latest series URL"""
    return get_latest(_id=_id)["href"]
    
def lookup_json(url):
    """fetch and decode json from an api"""
    session=requests.Session()
    try:
        json_res=get_api_result(session,url)
    except requests.ConnectionError as e:
        print('Connection Error')
        raise ConnectionError
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

#def get_download_link(filter_id):
#    filter_url=f'{OUTPUT_URL}/{filter_id}'
#    print(filter_url)
#    resp=lookup_json(filter_url)
#    try:
#        downloads=resp['downloads']['csv']['href']
#        return downloads
#    except Exception as e:
#        print(e)
#        return None

#def api_download(filter_id=FILTER_ID):
#    if not filter_id:
#        resp=post_api(url=POST_URL+'?submitted=true',params=EG)
#        FILTER_ID=resp['filter_id']
#        filter_id=FILTER_ID
#        print(f'Filter_id: {filter_id}')
#        print(resp)
#    
#    csv_link=get_download_link(filter_id)
#    if csv_link:
#        r = requests.get(csv_link)
#        return r
#        text = r.iter_lines()
#        reader = csv.reader(text, delimiter=',')
#        return reader
#    return None
#    #?submitted=true

def post_api(url=POST_URL,params=EG):
    """put request return json"""
    session=requests.Session()
    data=json.dumps(params)
    json_res=post_api_result(session,url,data)
    try:
        content=json.loads(json_res)
        return content
    except:
        raise NoContent


def post_api_result(session,url,params):
    """return content of a put request"""
    try:
        res=session.post(url, data=params)
        print(res)
        if res.status_code == 404:
            raise NotFound("URL {} not found".format(url))
    except Exception as e:
        print(e)
        return None
    return res.content
	

    
def lookup_index(series=''):
    """get up details of an ONS series"""
    url=MASTER_URL
    content=lookup_json(url)
    
    if series:
        serieslist=[i for i in content['items'] if i['id']==series]
    
    else:
        serieslist=[(i['title'],i['id']) for i in content['items']]
    
    return serieslist


def lookup_weeklydeaths():
    """specific details of weekly deaths"""
    r = lookup_index(series="weekly-deaths-local-authority")
    return r	

def get_options(series=ID,dimension="geography",url=""):
    """pull options for a specific dimension"""
    if not url:
        url=get_latest_url(_id=series)
    options_url=f"{url}/dimensions/{dimension}/options"
    content=lookup_json(options_url)
    _items=content['items']
    ids=[i['option'] for i in _items]
    return ids

def get_dimensions(_id=ID,url=""):
    """get dimensions of an ONS series"""
    if not url:
        url=get_latest_url(_id=_id)
    url=url+"/dimensions"
    
    content=lookup_json(url)
    _items=content['items']
    ids=[(i['name'],i['label']) for i in _items]
    return ids

def correct_dates():
    l=[]
    count=0
    rv=rev_week()
    for x in CovidWeek.objects.filter(nation='Wales'):
        _date=x.date-timedelta(2)
        print(_date)
        this=(_date.day,_date.month,_date.year)
        lookup=rv.get(this)
        if lookup:
            x.date=_date
            x.save()
            count+=1
    print(f'{count} updated')
        
def rev_week():
    x={}
    for key in weeks:
        x[weeks[key]]=key
    return x
    
    
    