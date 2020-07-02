# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
#from configs import config
from django.contrib.auth.models import Group, User

# Create your models here.


class CovidWeek(models.Model):
    areacode=models.CharField('area_code',max_length=200,default='')
    areaname=models.CharField('areaname',max_length=200,default='')
    nation=models.CharField('areaname',max_length=50,default='')
    date=models.DateTimeField('date',blank=True)
    weeklydeaths=models.IntegerField('weekly_deaths',default=0)
    totcumdeaths=models.IntegerField('cum_deaths',default=0)
    weeklycases= models.IntegerField('weekly_cases',default=0)
    totcumcases= models.IntegerField('cum_cases',default=0)
    estcasesweekly= models.IntegerField('est_cases_weekly',default=0)
    
    def __str__(self):
        return f"{self.areacode}: {self.date} cases: {self.estcasesweekly}"

