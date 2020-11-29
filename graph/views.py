# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import CovidWeek
import logging,json
from . import ons_fetch, model_calcs, ons_week
from utils import time_utils
import configs
from configs import userconfig

log = logging.getLogger('api.graph.views')
places=ons_week.make_index()

def index(request,place='index'):
    log.info('loading page')
    
    rates=model_calcs.output_rates()
    try:
        PHEstored=configs.config.get('PHE')
        edition=PHEstored.get('latest_update')
        lastupdate=time_utils.parseISO(edition).date()
        lastupdate_str=f'{lastupdate: %a %d %b}'
        last_cases=f'{lastupdate-model_calcs.DELAY: %a %d %b}'
        
    except Exception as e:
        log.error(e)
        lastupdate=None

    
    if place=='index':
        regions=model_calcs.sort_rate(model_calcs.output_rates(subset=ons_week.REGIONS))
        nations=model_calcs.output_rates(subset=ons_week.NATIONS)
        districts=model_calcs.sort_rate(model_calcs.output_rates(exclude=ons_week.NATIONS+ons_week.REGIONS,subset=ons_week.stored_names.values()))
        top_districts=model_calcs.top_rate(districts)
        
        return render(request,'graph/covid_chart_index.html',{'api_status':'true',
        	'last_update':lastupdate_str,'last_cases':last_cases,
        	'covid_rates':rates, 'regions':regions, 'nations':nations,'districts':districts,'top_districts':top_districts, "england_select":ons_week.england_select,"wales_select":ons_week.wales_select,"scotland_select":ons_week.scotland_select,"ni_select":ons_week.ni_select})
    	
    try:
        areacode=places[place]
        nation=ons_week.nation[areacode]
        nation_index=['England','Wales','Scotland','Northern Ireland','England and Wales'].index(nation)+1
        log.info(f'loading: {areacode} in {nation} ({nation_index})')
    except Exception as e:
    	log.error(e)
    	nation=None
    	areacode=None
    	nation_index=1
    return render(request,'graph/covid_chart_map.html',{'last_update':lastupdate_str,'last_cases':last_cases,'place':place, 'nation':nation, 'nation_index':nation_index,'areacode':areacode,'api_status':'true', 'covid-rates':rates, "england_select":ons_week.england_select,"wales_select":ons_week.wales_select,"scotland_select":ons_week.scotland_select,"ni_select":ons_week.ni_select})

def index_m(request,place='Birmingham'):
    return render(request,'graph/delays.html',{'place':place, 'api_status':'false','covid-rates':model_calcs.output_rates()})

def api(request,place=""):
    print(place)
    dataset=model_calcs.output_district(place)
    try:
        areacode=places[place]
        nation=ons_week.nation[areacode]
        nation_index=['England','Wales','Scotland','Northern Ireland'].index(nation)+1
        print(f'loading: {areacode} in {nation} ({nation_index})')
    except:
        nation=None
        areacode=None
        nation_index=1
    jsonresponse={'error':False,'place':place,'nation':nation, 'nation_index':nation_index,'areacode':areacode,'dataset':dataset}    
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
	
	
