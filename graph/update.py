# -*- coding: utf-8 -*- 
import os, logging
from .models import CovidWeek, CovidScores,AverageWeek
from . import ons_fetch,model_calcs,phe_fetch,scotland,import_csv,n_ireland,infections,wales,phe_deaths
from django.db.models import Sum
from .ons_week import stored_names
log = logging.getLogger('api.graph.update')


#constant files:
POP_FILE="ONS_UK_pop.csv"
EW_AV_FILE="ONSaverages_20152019.csv"
SCOT_AV_FILE="Scotland_averages_15-19_data.csv"
EW_REGIONS_AV_FILE="5Ydeaths_ONS_EnglishRegions_registrations.xlsx"
#https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/adhocs/11969fiveyearaveragenumberofweeklydeathregistrationsbyagegroupenglishregionsandwales2015to2019
DATA_STORE=model_calcs.DATA_STORE

"""
TO LOAD UP THIS DATABASE:

u=Updater()

u.load_constants()   >>> to load up population and 5-year averages.

u.process()   >> download and install up to date covid deaths and cases



data glitches:  #TO DO AUTO FIXING OF GLITCHES
MISSING AVERAGES FOR N IRELAND

Isles of Scilly sometimes part of Cornwall and Isles of Scilly
City of London soemetimes part of Hackney and City of London


"""
class Updater():
    def __init__(self):
        #self.checks()
        pass
        
    def checks(self):
        """check population data and excess deaths calcs"""
        for name in stored_names.values():
            try:
                q=CovidScores.objects.get(areaname=name)
            except:
                log.error(f'data for {name} missing')
                break
            try:
                assert q.population is not None
            except Exception as e:
                log.info(f'population data for {name} missing')
            try:
                assert q.excess_deaths is not None
            except Exception as e:
                log.info(f'excess death calculation for {name} missing')
                
                
        for areacode in stored_names.keys():
            try:
                q=AverageWeek.objects.filter(areacode=areacode)
                if not q:
                    log.info(f'Average 5 years data for {stored_names[areacode]} missing')  
            except Exception as e:
                log.info(e)        
        av_h=AverageWeek.objects.filter(weeklyhospitaldeaths__isnull=True).count()
        av_all=AverageWeek.objects.all().count()
        av_deaths=AverageWeek.objects.filter(weeklyalldeaths__isnull=True).count()
        log.info(f"Average data : av. hospital data MISSING in {av_h} places, all deaths data MISSING in {av_deaths} places out of {av_all} all places")
        
    
#    def check_cases(self):
#        
        
        
    def process(self):
        """check for updates of deaths and cases data & download updates"""
        
        update_deaths,update_regions=False,False
        
        log.info('Checking ONS for weekly deaths update - normally released Tuesday')
        try:
            wz=ons_fetch.ONS_Importer()
            if wz.process(): #import and parse if new data available
                update_deaths=True
                
            wr=ons_fetch.ONS_Regions()
            if wr.process():
                update_regions=True
                
        except Exception as e:
            log.error(e)
            log.error('Failed to check ONS weekly deaths')
                
        log.info('Updating Scottish deaths - normally released Wednesday')
        
        try:
            self.scot=scotland.Scot_Importer()
            if self.scot.update_check():
                self.scot.process()
                update_deaths=True
        except Exception as e:
            log.error(e)
            log.error('Failed to update Scottish deaths')
        
        log.info('Updating N Irish deaths')
        try:
            ni=n_ireland.NI_Importer()
            ni.process()
            if ni.check_update():
               ni.parse()
               update_deaths=True
        except Exception as e:
            log.error(e)
            log.error('Failed to update N Irish deaths')
        


        #READJUST HERE FOR ANY GLITCHES


        
        log.info('Checking PHE deaths from API - England and Wales - released daily')
        try:
            #UPDATE PHE DEATHS
            pd=phe_deaths.PHE_Deaths()
            pd.process()
        except Exception as e:
            log.error(e)        

        log.info('Checking PHE cases - England and Wales - released daily')
        
        try:
            cz=phe_fetch.Fetch_API()
            cz.process()
            log.info('PHE cases data successfully processed')
        except Exception as e:
            log.error(e)
            log.error('PHE API failure ... using old CSV')
            try:
                cz=phe_fetch.Fetch_PHE()
                cz.process()
                cz.save()
            except Exception as e:
                log.error(e)                
                
#        #Welsh daily cases now on PHE API
        try:
            wck=wales.Wales_Check()
            if wck._update:
                log.info('Updating Welsh cases')
                wz=wales.Wales_Cases()
                wz.process()
        except Exception as e:
            log.error(e)   
#        self.cz.update_totals()

        try:
            log.info('Updating Scottish cases - released daily')
            self.scot2=scotland.Scot_Cases()
            self.scot2.process()
        except Exception as e:
            log.error(e)   
        
        
        
        log.info('Update new case rates')
        
        try:
            model_calcs.calc_newcases_rates()
        except Exception as e:
            log.error(e)   

        if update_deaths or update_regions:
            try:
                log.info('Updating cumulative deaths')
                model_calcs.update_cum_deaths()
    
                log.info('Updating excess deaths')
                self.check_excess()
                model_calcs.calc_excess_rates()
                
                
                log.info('Updating Reuters infection curve')
                infections.calc()
            except Exception as e:
                log.error(e)

        
        log.info('Updates complete')


    def load_constants(self):
        
        #all UK population
        import_csv.AddPop(os.path.join(DATA_STORE,POP_FILE))
        
        #add average deaths
        #England and Wales
        aa=import_csv.AddAverages(os.path.join(DATA_STORE,EW_AV_FILE))
        aa.total_averages()

        ons_fetch.correct_smallpops() #merge small places and deal with corrected geographies
        
        #add E+W regions
        ar=import_csv.AddRegions(os.path.join(DATA_STORE,EW_REGIONS_AV_FILE))
        ar.process()
        
        #Scotland
        sa=scotland.Scot_Average()
        sa.process(os.path.join(DATA_STORE,SCOT_AV_FILE))
        sa.parse()
        sa.sum_Scotland()
        
        #Ireland

    def check_excess(self):
        model_calcs.excess_deaths()

def update():
    u=Updater()
    u.process()

def sums():
    weeks=[w['date'] for w in CovidWeek.objects.values('date').distinct().order_by('date')]
    log.info(f'Total weeks: {len(weeks)}')
    log.info([f"{w:%d/%m}" for w in weeks])
    nations=nations_list()
    nations_set=nations_filter()
    for nation in nations:
        log.info(nation)
        for week in weeks:
            _set=nations_set[nation]
            _thisweek=_set.filter(date=week)
            deathtoll=_thisweek.aggregate(Sum('weeklyalldeaths'))['weeklyalldeaths__sum']
            c19deaths=_thisweek.aggregate(Sum('weeklydeaths'))['weeklydeaths__sum']
            #deathtoll=sum([i.weeklyalldeaths for i in _thisweek])
            log.info(f'{nation} week ending {week:%d/%m} deaths: {deathtoll}  COVIDdeaths: {c19deaths}')

def nations_list():
    return ['England','Wales','Scotland','Northern Ireland']

def nations_filter():
    nations=nations_list()
    nations_set= {}
    for nation in nations:
        nations_set[nation]=CovidWeek.objects.filter(nation=nation)
    return nations_set
    
    
