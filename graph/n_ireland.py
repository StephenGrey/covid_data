import pandas,requests
from .ons_week import ni_codes, week as ons_week,sunday, stored_names
from .models import CovidWeek


import configs
from configs import userconfig

DEATHS_URL="https://www.nisra.gov.uk/sites/nisra.gov.uk/files/publications/Weekly_Deaths.xls"

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
        pass
        
    def check_update(self):
        niupdate=configs.config.get('NIreland')
        if niupdate:
            self.last_update=niupdate.get('latest_deaths')
            if str(self.edition)==self.last_update:
                print('NI deaths: up to date')
                return False
        print('NI deaths - update available')
        return True
        
    def fetch_excel(self,url=DEATHS_URL):
        f=requests.get(url)
        xl=f.content if f else None
        self.open_excel(xl)
        self.edition=self.data['Week Ending (Friday)'].max()
        
    def open_excel(self,path):
        self.data=pandas.read_excel(path,sheet_name="Table 5",skiprows=4).dropna() # covid deaths
        self.data2=pandas.read_excel(path,sheet_name="Table 3",skiprows=4).dropna() #all deaths
        self.data3=pandas.read_excel(path,sheet_name="Table 7",skiprows=4).dropna() #care home deaths
        
    def weeks(self):
        return sorted([int(z) for z in self.data2['Registration Week'].unique()])
        
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
        
        print(week,district)
        
        _allc19=zero_null(self.data[(self.data['Registration Week']==week)][district])
        _all=zero_null(self.data2[(self.data2['Registration Week']==week)][district])
        careh19=zero_null(self.data3[(self.data3['Registration Week']==week)][district])
        
        qrow=CovidWeek.objects.filter(week=week+1,areacode=areacode) # week +1 to bring in line with ONS weeks.
        if qrow:
            row=qrow[0]
            if _update:
                change=False
                print(f"stored weekly C19 deaths: {row.weeklydeaths}")
                if row.weeklydeaths !=_allc19:
                    print(f'update total C19 deaths from {row.weeklydeaths} to {_allc19}')
                    row.weeklydeaths=_allc19
                    change=True
                if row.weeklyalldeaths != _all:
                    print(f'update total all deaths from {row.weeklyalldeaths} to {_all}')
                    row.weeklyalldeaths=_all
                    change=True
                if row.weeklyC19carehomedeaths != careh19:
                    print(f'update total C19 care home deaths from {row.weeklyC19carehomedeaths} to {careh19}')
                    row.weeklyC19carehomedeaths=careh19
                    change=True
                row.save() if change else None
        else:
            if _update:
                areaname=stored_names[areacode]
                _nation='Northern Ireland'
                row=CovidWeek(week=week+1,areacode=areacode,nation=_nation,areaname=areaname)
                print(f'Created week {sunday(week)} for {district}')
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
    