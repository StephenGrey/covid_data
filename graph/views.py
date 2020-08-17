# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import CovidWeek
import logging,json
from . import ons_fetch, model_calcs

log = logging.getLogger('api.graph.views')

def index(request,place='Birmingham'):
    return render(request,'graph/covid_chart2.html',{'place':place, 'api_status':'true', 'covid-rates':model_calcs.output_rates()})

def index_m(request,place='Birmingham'):
    return render(request,'graph/testmap.html',{'place':place, 'api_status':'false','covid-rates':model_calcs.output_rates()})

def api(request,place=""):
	print(place)
	dataset=model_calcs.output_district(place)
#	district=CovidWeek.objects.filter(areaname=place,date__range=["2020-02-14", "2020-06-12"])
#	totalcumdeaths=[i.totcumdeaths for i in district]
#	weeklydeaths=[i.weeklydeaths for i in district]
#	weeklycases=[i.weeklycases for i in district]
#	estcasesweekly=[i.estcasesweekly for i in district]
#	dataset={ 
#			1:{'label':"Reuters estimate- new infections ",'data':estcasesweekly},
#			2:{'label':'Total Deaths','data':totalcumdeaths},
#			3:{'label':'Covid-Positive Tests','data':weeklycases},
#			4:{'label':"Weekly deaths",'data':weeklydeaths},
#	}
	jsonresponse={'error':False, 'place':place,'dataset':dataset}    
	return JsonResponse(jsonresponse)

def api_rates(request):
	dataset=model_calcs.output_rates()
	jsonresponse={'error':False, 'dataset':dataset}    
	return JsonResponse(jsonresponse)


def api_shapes(request):
	return HttpResponse(shapes)

def fetch_ons(request,place=""):
	print('fetch ons')
	dataset=ons_fetch.lookup_ons("some query")
	print(dataset)
	jsonresponse={'error':False, 'place':place,'dataset':dataset}    
	return JsonResponse(dataset)