# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
#from configs import config
from django.contrib.auth.models import Group, User

# Create your models here.

class DailyCases(models.Model):
    areacode=models.CharField('area_code',max_length=200,default='')
    areaname=models.CharField('areaname',max_length=200,default='')
    specimenDate=models.DateTimeField('date',blank=True)
    dailyLabConfirmedCases=models.IntegerField('dailyLabConfirmedCases',blank=True,null=True)
    previouslyReportedDailyCases=models.IntegerField('previouslyReportedDailyCases',blank=True,null=True)
    changeInDailyCases=models.IntegerField('changeInDailyCases',blank=True,null=True)
    totalLabConfirmedCases=models.IntegerField('totalLabConfirmedCases',blank=True,null=True)
    previouslyReportedTotalCases=models.IntegerField('previouslyReportedTotalCases',blank=True,null=True)
    changeInTotalCases=models.IntegerField('changeInTotalCases',blank=True,null=True)
    dailyTotalLabConfirmedCasesRate=models.DecimalField('dailyTotalLabConfirmedCasesRate',max_digits=7, decimal_places=1,blank=True,null=True)


class CovidScores(models.Model):
    areaname=models.CharField('areaname',max_length=200,default='')
    excess_deaths=models.IntegerField('estimated_excess_deaths',blank=True,null=True)
    excess_deaths_carehomes=models.IntegerField('estimated_carehomes_excess_deaths',blank=True,null=True)
    population=models.IntegerField('population',blank=True,null=True)
    excess_death_rate=models.DecimalField('excess_death_rate',max_digits=7, decimal_places=1,blank=True,null=True)


class CovidWeek(models.Model):
    areacode=models.CharField('area_code',max_length=200,default='')
    areaname=models.CharField('areaname',max_length=200,default='')
    nation=models.CharField('areaname',max_length=50,default='')
    date=models.DateTimeField('date',blank=True)
    weeklydeaths=models.IntegerField('weekly_deaths',blank=True,null=True)
    weeklyalldeaths=models.IntegerField('weekly_all_deaths',blank=True,null=True)
    weeklyC19hospitaldeaths=models.IntegerField('weekly_covid_hospital_deaths',blank=True,null=True)
    weeklyhospitaldeaths=models.IntegerField('weekly_hospital_deaths',blank=True,null=True)
    weeklyC19carehomedeaths=models.IntegerField('weekly_covid19_carehome_deaths',blank=True,null=True)
    weeklycarehomedeaths=models.IntegerField('weekly_carehome_deaths',blank=True,null=True)
    totcumdeaths=models.IntegerField('cum_deaths',default=0,blank=True,null=True)
    weeklycases= models.IntegerField('weekly_cases',default=0,null=True,blank=True)
    totcumcases= models.IntegerField('cum_cases',default=0,null=True,blank=True)
    estcasesweekly= models.IntegerField('est_cases_weekly',blank=True,null=True)
    estinfectionscum=models.IntegerField('est_cases_cum',blank=True,null=True)
    def __str__(self):
        return f"{self.areacode}: {self.date} cases: {self.estcasesweekly}"

class AverageWeek(models.Model):
    """for storing 5 year averages"""
    areacode=models.CharField('area_code',max_length=50)
    week=models.IntegerField('week_number')
    weeklyalldeaths=models.DecimalField('weekly_all_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyhospitaldeaths=models.DecimalField('weekly_hospital_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklycarehomedeaths=models.DecimalField('weekly_care_home_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyhomedeaths=models.DecimalField('weekly_home_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyhospicedeaths=models.DecimalField('weekly_hospice_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyelsewheredeaths=models.DecimalField('weekly_elsewhere_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyothercommunaldeaths=models.DecimalField('weekly_other_communal_deaths',max_digits=7, decimal_places=1,blank=True,null=True)

    def __str__(self):
        return f"{self.areacode}: {self.date} cases: {self.estcasesweekly}"

