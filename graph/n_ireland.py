import pandas,requests,logging
from .ons_week import ni_codes, week as ons_week,sunday, stored_names,week_lookup
from .models import CovidWeek
log = logging.getLogger('api.graph.n_ireland')

import configs
from configs import userconfig

DEATHS_URL="https://www.nisra.gov.uk/sites/nisra.gov.uk/files/publications/Weekly_Deaths.XLSX"
INFO_URL="https://www.nisra.gov.uk/publications/weekly-deaths"
#old"https://www.nisra.gov.uk/sites/nisra.gov.uk/files/publications/Weekly_Deaths.xls"
#historic https://www.nisra.gov.uk/sites/nisra.gov.uk/files/publications/Weekly_Deaths%20-%20Historical.xls
"""
NI: YET TO PUBLISH LOCAL DEATHS BY OCCURRENCE

P Weekly published data are provisional.													
1 This data is based on registrations of deaths, not occurrences. The majority of deaths are registered within five days in Northern Ireland. 													
2 Data are assigned to LGD based on usual residence of the deceased, as provided by the informant. Usual residence can include a care home. Where the deceased was not usually resident in Northern Ireland, their death has been mapped to the place of death.		
NI deaths - weeks end on Friday; NI registration week is a week after ONS week.
So Week 1 ended 10/1 ; ONS week 1 ended 3/1											

"""

ni_codes_inv= {v: k for k, v in ni_codes.items()}

class NI_Importer():
    
    def process(self):
        #f
        self.fetch_excel()
        self.fix()
        
    def fix(self):
        self.data2['week']=self.data2['Week Ending (Friday)'].dt.date.apply(week_lookup)
        self.data['week']=self.data['Week Ending (Friday)'].dt.date.apply(week_lookup)
        self.data3['week']=self.data3['Week Ending (Friday)'].dt.date.apply(week_lookup)
        
    def check_update(self):
        niupdate=configs.config.get('NIreland')
        if niupdate:
            self.last_update=niupdate.get('latest_deaths')
            if str(self.edition)==self.last_update:
                log.info('NI deaths: up to date')
                return False
        log.info('NI deaths - update available')
        return True
        
    def fetch_excel(self,url=DEATHS_URL):
        f=requests.get(url)
        xl=f.content if f else None
        self.open_excel(xl)
        self.edition=self.data['Week Ending (Friday)'].max()
        
    def open_excel(self,path):
        self.data=pandas.read_excel(path,sheet_name="Table 6",skiprows=4).dropna() # covid deaths
        self.data2=pandas.read_excel(path,sheet_name="Table 3",skiprows=4).dropna() #all deaths
        self.data3=pandas.read_excel(path,sheet_name="Table 8",skiprows=4).dropna() #care home deaths
        
    def weeks(self):
        return sorted([int(z) for z in self.data2['week'].unique()])
        
    def districts(self):
        return ni_codes.keys()
        
    def areacodes(self):
        return ni_codes.values()
        
    def parse(self):
        for areacode in self.areacodes():
            for week in self.weeks():
                self.parse_week(week,areacode)
        if self.edition:
            configs.userconfig.update('NIreland','latest_deaths',str(self.edition))

    def parse_week(self,week,areacode,_update=True):
        district=ni_codes_inv[areacode] #different syntax on import
        
        if district=='Northern Ireland':
        	district='Total'
        
        #print(week,district)
        
        _allc19=zero_null(self.data[(self.data['week']==week)][district])
        _all=zero_null(self.data2[(self.data2['week']==week)][district])
        careh19=zero_null(self.data3[(self.data3['week']==week)][district])
        
        qrow=CovidWeek.objects.filter(week=week+1,areacode=areacode) # week +1 to bring in line with ONS weeks.
        if qrow:
            row=qrow[0]
            if _update:
                change=False
                #log.debug(f"stored weekly C19 deaths: {row.weeklydeaths}")
                if row.weeklydeaths !=_allc19:
                    log.info(f'week {week} update total C19 deaths in {district} from {row.weeklydeaths} to {_allc19}')
                    row.weeklydeaths=_allc19
                    change=True
                if row.weeklyalldeaths != _all:
                    log.info(f'week {week} update total all deaths in {district} from {row.weeklyalldeaths} to {_all}')
                    row.weeklyalldeaths=_all
                    change=True
                if row.weeklyC19carehomedeaths != careh19:
                    log.info(f'week {week} update total C19 care home deaths in {district} from {row.weeklyC19carehomedeaths} to {careh19}')
                    row.weeklyC19carehomedeaths=careh19
                    change=True
                row.save() if change else None
        else:
            if _update:
                areaname=stored_names[areacode]
                _nation='Northern Ireland'
                row=CovidWeek(week=week+1,areacode=areacode,nation=_nation,areaname=areaname)
                log.info(f'Created week {sunday(week)} for {district}')
                row.weeklydeaths=_allc19
                row.weeklyalldeaths=_all
                row.save()


def valid_int(s):
    try:
        n=int(s)
        return n
    except:
        return None
    
    
def zero_null(s):
    try:
        n=int(s)
        return n
    except:
        return 0
    