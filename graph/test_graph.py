from django.test import TestCase
#from django.contrib.auth.models import User, Group, Permission
#from django.core.management.base import BaseCommand, CommandError
#try:
#    from django.core.urlresolvers import reverse,resolve
#except ImportError:
#    from django.urls import reverse,resolve,NoReverseMatch
from graph.models import CovidWeek
from graph import ons_week,model_calcs
#from documents.management.commands import setup
#from documents.management.commands.setup import make_admin_or_login
#from documents import solrcursor
#from django.test.client import Client
import logging,re,os,json
log = logging.getLogger('api.tests')
from django.contrib.staticfiles import finders

DATA_STORE=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../data'))



class GraphTest(TestCase):
    def setUp(self):
        
        pass
        

class MapTest(GraphTest):
    
    def test_coverage(self):
        log.info('test')
        map_path = finders.find(model_calcs.MAP_PATH)
        self.assertTrue(os.path.exists(map_path))
        
        with open(map_path) as json_file:
            mapdata = json.load(json_file)
        self.assertTrue('UK_corrected' in mapdata.get('objects'))
        coverage=([x.get('properties')['areacode'] for x in mapdata.get('objects').get('UK_corrected').get('geometries')])
        

        for areacode in ons_week.stored_names.keys():
            try:
                coverage.remove(areacode)
            except ValueError:
                #Bournemouth, Christchurch and PPoole
                print(areacode)
                knownmissing=[]
#                
#        'E06000058',
#		'E06000059', #Dorset
#'E06000060', #Buckinghamshire
#'E07000244', #East Suffolk
#'E07000245', #West Suffolk
#'E07000246', #Somerset West and Taunton
#'S08000015',
#'S08000016',
#'S08000017',
#'S08000019',
#'S08000020',
#'S08000022',
#'S08000024',
#'S08000025',
#'S08000026',
#'S08000028',
#'S08000029',
#'S08000030',
#'S08000031',
#'S08000032']
                self.assertTrue(areacode in knownmissing)
                

    
    
    	
    	