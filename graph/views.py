# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import CovidWeek
import logging,json

log = logging.getLogger('api.graph.views')

def index(request):
    return render(request,'graph/local_covid.html')

def api(request,place=""):
	print(place)
	district=CovidWeek.objects.filter(areaname=place,date__range=["2020-02-14", "2020-06-12"])
	totalcumdeaths=[i.totcumdeaths for i in district]
	weeklydeaths=[i.weeklydeaths for i in district]
	weeklycases=[i.weeklycases for i in district]
	estcasesweekly=[i.estcasesweekly for i in district]
	dataset={ 
			1:{'label':"Estimate- new infections ",'data':estcasesweekly},
			2:{'label':'Total Deaths','data':totalcumdeaths},
			3:{'label':'Covid-Positive Tests','data':weeklycases},
			4:{'label':"Weekly deaths",'data':weeklydeaths},
	}
	jsonresponse={'error':False, 'place':place,'dataset':dataset}    
	return JsonResponse(jsonresponse)
