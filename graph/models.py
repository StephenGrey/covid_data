# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import Group, User

class DailyReport(models.Model):
    areacode=models.CharField('area_code',db_index=True,max_length=200,default='')
    specimenDate=models.DateTimeField('date',db_index=True)
    dailycases=models.IntegerField('dailyLabConfirmedCases',blank=True,null=True)
    add_cases=models.IntegerField('add_cases',blank=True,null=True)
    publag=models.IntegerField('publication_delay',db_index=True)
    class Meta:
        indexes = [
            models.Index(fields=['areacode']),
            models.Index(fields=['specimenDate']),
            models.Index(fields=['publag']),
        ]


class DailyCases(models.Model):
    areacode=models.CharField('area_code',db_index=True,max_length=200,default='')
    areaname=models.CharField('areaname',db_index=True,max_length=200,default='')
    specimenDate=models.DateTimeField('date',db_index=True,blank=True)
    dailyLabConfirmedCases=models.IntegerField('dailyLabConfirmedCases',blank=True,null=True)
    previouslyReportedDailyCases=models.IntegerField('previouslyReportedDailyCases',blank=True,null=True)
    changeInDailyCases=models.IntegerField('changeInDailyCases',blank=True,null=True)
    totalLabConfirmedCases=models.IntegerField('totalLabConfirmedCases',blank=True,null=True)
    previouslyReportedTotalCases=models.IntegerField('previouslyReportedTotalCases',blank=True,null=True)
    changeInTotalCases=models.IntegerField('changeInTotalCases',blank=True,null=True)
    dailyTotalLabConfirmedCasesRate=models.DecimalField('dailyTotalLabConfirmedCasesRate',max_digits=7, decimal_places=1,blank=True,null=True)
    cases_lag=models.CharField('cases_lag',max_length=200,default='',null=True)
    
    deaths=models.IntegerField('deaths',blank=True,null=True)
    published_deaths=models.IntegerField('published_deaths',blank=True,null=True)
    total_published_deaths=models.IntegerField('total_published_deaths',blank=True,null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['areacode']),
            models.Index(fields=['areaname']),
            models.Index(fields=['specimenDate']),
        ]


class CovidScores(models.Model):
    areaname=models.CharField('areaname',db_index=True,max_length=200,default='')
    excess_deaths=models.IntegerField('estimated_excess_deaths',blank=True,null=True)
    excess_deaths_carehomes=models.IntegerField('estimated_carehomes_excess_deaths',blank=True,null=True)
    population=models.IntegerField('population',blank=True,null=True)
    excess_death_rate=models.DecimalField('excess_death_rate',max_digits=7, decimal_places=1,blank=True,null=True)
    latest_case_rate=models.DecimalField('latest_case_rate',max_digits=7, decimal_places=1,blank=True,null=True)
    change_case_rate=models.DecimalField('change_case_rate',max_digits=7, decimal_places=1,blank=True,null=True)
    last_month_PHEdeaths=models.IntegerField('last month deaths',blank=True,null=True)
    wave2_PHEdeaths=models.IntegerField('wave2 deaths',blank=True,null=True)    
    wave2_deathrate=models.DecimalField('wave2_death_rate',max_digits=7, decimal_places=1,blank=True,null=True)

    class Meta:
        indexes = [
            models.Index(fields=['areaname']),
        ]


class CovidWeek(models.Model):
    areacode=models.CharField('area_code',db_index=True,max_length=200,default='')
    areaname=models.CharField('areaname',db_index=True,max_length=200,default='')
    nation=models.CharField('nation',db_index=True,max_length=50,default='')
    date=models.DateTimeField('date',blank=True,null=True)
    week=models.IntegerField('week',db_index=True,blank=True) #use ONS standard week
    weeklydeaths=models.IntegerField('weekly_deaths',blank=True,null=True)
    weeklyalldeaths=models.IntegerField('weekly_all_deaths',blank=True,null=True)
    weeklyC19hospitaldeaths=models.IntegerField('weekly_covid_hospital_deaths',blank=True,null=True)
    weeklyhospitaldeaths=models.IntegerField('weekly_hospital_deaths',blank=True,null=True)
    weeklyC19carehomedeaths=models.IntegerField('weekly_covid19_carehome_deaths',blank=True,null=True)
    weeklycarehomedeaths=models.IntegerField('weekly_carehome_deaths',blank=True,null=True)
    totcumdeaths=models.IntegerField('cum_deaths',default=None,blank=True,null=True)
    weeklycases= models.IntegerField('weekly_cases',default=None,null=True,blank=True)
    totcumcases= models.IntegerField('cum_cases',default=None,null=True,blank=True)
    estcasesweekly= models.IntegerField('est_cases_weekly',blank=True,null=True)
    estinfectionscum=models.IntegerField('est_cases_cum',blank=True,null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['areacode']),
            models.Index(fields=['areaname']),
            models.Index(fields=['nation']),
            models.Index(fields=['week']),
        ]
    def __str__(self):
        return f"{self.areacode}: {self.date} cases: {self.weeklycases}"

class AverageWeek(models.Model):
    """for storing 5 year averages"""
    areacode=models.CharField('area_code',db_index=True,max_length=50)
    week=models.IntegerField('week_number',db_index=True)
    weeklyalldeaths=models.DecimalField('weekly_all_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyhospitaldeaths=models.DecimalField('weekly_hospital_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklycarehomedeaths=models.DecimalField('weekly_care_home_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyhomedeaths=models.DecimalField('weekly_home_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyhospicedeaths=models.DecimalField('weekly_hospice_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyelsewheredeaths=models.DecimalField('weekly_elsewhere_deaths',max_digits=7, decimal_places=1,blank=True,null=True)
    weeklyothercommunaldeaths=models.DecimalField('weekly_other_communal_deaths',max_digits=7, decimal_places=1,blank=True,null=True)

    class Meta:
        indexes = [
            models.Index(fields=['areacode']),
            models.Index(fields=['week']),
        ]

    def __str__(self):
        return f"{self.areacode}: {self.week} average deaths: {self.weeklyalldeaths}"


