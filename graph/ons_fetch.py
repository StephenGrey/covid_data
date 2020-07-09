import requests,json
from .ons_week import week,sunday
from .models import CovidWeek

ID="weekly-deaths-local-authority"
MASTER_URL="https://api.beta.ons.gov.uk/v1/datasets"
TIMEOUT=20


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
                content=lookup_json('',url)
                for i in content['observations']:
                    field=f"{placeofdeath}_{i['dimensions']['causeofdeath']['id']}"
                    week_data[field]=int(i['observation'])
            week_data['all_covid']=week_data['home_covid-19']+week_data['care-home_covid-19']+week_data['elsewhere_covid-19']+week_data['hospital_covid-19']+week_data['other-communal-establishment_covid-19']+week_data['hospice_covid-19']
            #print(week_data['all_covid'])
            week_data['total_allcauses']=week_data['care-home_all-causes']+week_data['elsewhere_all-causes']+week_data['home_all-causes']+week_data['hospice_all-causes']+week_data['hospital_all-causes']+week_data['other-communal-establishment_all-causes']
            #print(week_data)
            qrow=CovidWeek.objects.filter(date=sunday(week),areacode=geography)
            row=next(iter(qrow), None)
            if row:
                _update=False
                print(f"stored weekly deaths: {row.weeklydeaths}")
                _all=week_data['all_covid']
                if row.weeklydeaths !=_all:
                    print(f'update total covid deaths from {row.weeklydeaths} to {_all}')
                    _update=True
                    row.weeklydeaths=_all
                    row.save()
                
                hosp19=week_data['hospital_covid-19']
                if row.weeklyC19hospitaldeaths !=hosp19:
                    _update=True
                    print(f'updating hospital C19 from {row.weeklycarehomedeaths} to {hosp19}')
                    row.weeklyC19hospitaldeaths=hosp19
                
                careh=week_data['care-home_all-causes']
                if row.weeklycarehomedeaths !=careh:
                    _update=True
                    print(f'updating care home deaths from {row.weeklycarehomedeaths} to {careh}')
                    row.weeklycarehomedeaths=careh
                
                careh19=week_data['care-home_covid-19']
                if row.weeklyC19carehomedeaths !=careh19:
                    _update=True
                    print(f'updating care home C19 deaths from {row.weeklycarehomedeaths} to {careh19}')
                    row.weeklyC19carehomedeaths=careh19
                
                _all=week_data['total_allcauses']
                if row.weeklyalldeaths !=_all:
                    _update=True
                    print(f'updating all deaths from {row.weeklyalldeaths} to {_all}')
                    row.weeklyalldeaths=_all
                
                if _update:
                    row.save()
            data[week]=week_data
        except Exception as e:
            print(e)
            print('week failed')

    return data

def get_latest(_id=ID):
    """latest details of ONS series"""
    info=lookup_index(series=_id)[0]
    return info['links']['latest_version'] #.keys() #['latest_version']

def get_latest_url(_id=ID):
    """latest series URL"""
    return get_latest(_id=_id)["href"]
    
def lookup_json(query,url):
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

    
def lookup_index(series=''):
    """get up details of an ONS series"""
    url=MASTER_URL
    content=lookup_json('',url)
    
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
    content=lookup_json('',options_url)
    _items=content['items']
    ids=[i['option'] for i in _items]
    return ids

def get_dimensions(_id=ID,url=""):
    """get dimensions of an ONS series"""
    if not url:
        url=get_latest_url(_id=_id)
    url=url+"/dimensions"
    
    content=lookup_json('',url)
    _items=content['items']
    ids=[(i['name'],i['label']) for i in _items]
    return ids


    
