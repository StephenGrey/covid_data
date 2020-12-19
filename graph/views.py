# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.cache import cache_page
import os,time
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
CACHED_DAILY_SERIES=model_calcs.output_daily_series(series='dailyLabConfirmedCases',n=30)
CACHE_UPDATED=time.time()

@cache_page(60 * 15)
def index(request,place='index'):
    log.info('loading page')
    
    rates=model_calcs.output_rates()
    try:
        PHEstored=configs.config.get('PHE')
        edition=PHEstored.get('latest_update')
        lastupdate=time_utils.parseISO(edition).date()
        lastupdate_str=f'{lastupdate: %a %d %b}'
        last_cases=f'{lastupdate-model_calcs.DELAY:%d %b}'
        
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

@cache_page(60 * 15)
def sparks(request):
    if True:
        regions=model_calcs.sort_rate(model_calcs.output_rates(subset=ons_week.REGIONS))
        nations=model_calcs.output_rates(subset=ons_week.NATIONS)
        districts=model_calcs.sort_rate(model_calcs.output_rates(exclude=ons_week.NATIONS+ons_week.REGIONS,subset=ons_week.stored_names.values()))
        top_districts=model_calcs.top_rate(districts)

    return render(request,'graph/sparks2.html',{'api_status':'true','regions':regions, 'nations':nations,'districts':districts,'top_districts':top_districts, "england_select":ons_week.england_select,"wales_select":ons_week.wales_select,"scotland_select":ons_week.scotland_select,"ni_select":ons_week.ni_select})

@cache_page(60 * 15)
def api(request,place=""):
    log.debug(place)
    dataset=model_calcs.output_district(place)
    try:
        areacode=places[place]
        nation=ons_week.nation[areacode]
        nation_index=['England','Wales','Scotland','Northern Ireland'].index(nation)+1
        log.debug(f'loading: {areacode} in {nation} ({nation_index})')
    except:
        nation=None
        areacode=None
        nation_index=1
    jsonresponse={'error':False,'place':place,'nation':nation, 'nation_index':nation_index,'areacode':areacode,'dataset':dataset}    
    return JsonResponse(jsonresponse)

@cache_page(60 * 15)
def api_rates(request):
	dataset=model_calcs.output_rates()
	jsonresponse={'error':False, 'dataset':dataset}    
	return JsonResponse(jsonresponse)

@cache_page(60 * 15)
def api_slim_data(request,place=""):
	"""return data on limited series"""
	_error=False
	try:
		PHEstored=configs.config.get('PHE')
		edition=PHEstored.get('latest_update')
	except:
		edition=None
		_error=True
	log.debug(place)
	dataset=model_calcs.output_slim_district(place)
	if not dataset:
		_error=True
	return JsonResponse({'error':_error, 'name':'select_data_for_area','place':place,'dataset':dataset, 'latest_update':edition})

@cache_page(60 * 15)		
def api_all_daily(request):
	_error=False
	try:
		PHEstored=configs.config.get('PHE')
		edition=PHEstored.get('latest_update')
	except:
		edition=None
		_error=True
	series='dailyLabConfirmedCases'
	dataset=CACHED_DAILY_SERIES
	if not dataset:
		_error=True
		
	res={'error':_error, 'name':'select_all_places_daily','series':series,'dataset':dataset, 'latest_update':edition}
	log.debug(res)
	return JsonResponse(res)
	
@cache_page(60 * 15)
def api_places(request):
	_error=False
	try:
		places=model_calcs.output_places()
	except:
		places=None
		_error=True
	return JsonResponse({'error':_error,'name':'index_of_areas','places':places})

@cache_page(60 * 15)	
def api_shapes(request):
	return HttpResponse(shapes)


def fetch_ons(request,place=""):
	print('fetch ons')
	dataset=ons_fetch.lookup_ons("some query")
	print(dataset)
	jsonresponse={'error':False, 'place':place,'dataset':dataset}    
	return JsonResponse(dataset)
	
	
