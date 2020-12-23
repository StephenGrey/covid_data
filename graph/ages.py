from . import phe_fetch
from collections import defaultdict
import matplotlib.pyplot as plt

AGE_RANGES=['80_to_84', '5_to_9', '85_to_89', '20_to_24', '30_to_34', '75_to_79', '60_to_64', '55_to_59', '45_to_49', '90+', '35_to_39', '15_to_19',  '40_to_44', '0_to_4', '10_to_14', '50_to_54', '65_to_69', '70_to_74', '25_to_29']
BAND1=['5_to_9','0_to_4', '10_to_14','15_to_19']
LABEL1='0-19 Yrs'
LABEL2='20-69 Yrs'
LABEL3='70+ Yrs'
BAND3=['80_to_84','75_to_79','90+','70_to_74',]
BAND2=['20_to_24','25_to_29','30_to_34','35_to_39','40_to_44','45_to_49','50_to_54', '55_to_59','60_to_64', '65_to_69']
PLACE='South East'

def rates(place=PLACE):
    z=phe_fetch.Fetch_API()
    z.api.structure={'specimenDate': 'date', 'areaName': 'areaName', 'areaCode': 'areaCode', 'maleCases':'maleCases','femaleCases':'femaleCases'}
    z.api.filters=z.district_filter(place)  
    ages=z.api.get_json()    
    data=ages.get('data')
    
    rate_series= defaultdict(list)
    for day in data:
    	day_rates={}
    	date=day.get('specimenDate')
    	
    	band1,band2,band3=0,0,0
    	
    	male_rates=day.get('maleCases')
    	for item in male_rates:
    		_range=item.get('age')
    		_rate=item.get('value')
    		
    		if _range in BAND1:
    			band1+=_rate
    		elif _range in BAND2:
    			band2+=_rate
    		else:
    			band3+=_rate
    			#rate_series[_range+'_MALE'].append((_rate,date))
    	female_rates=day.get('femaleCases')
    	for item in female_rates:
    		_range=item.get('age')
    		_rate=item.get('value')
    		if _range in BAND1:
    			band1+=_rate
    		elif _range in BAND2:
    			band2+=_rate
    		else:
    			band3+=_rate    		
    		
    	_all=band1+band2+band3	
    	rate_series[date]=band1,band2,band3
    		#rate_series[_range+'_FEMALE'].append((_rate,date))
    	
    return rate_series





def new_cases(place=PLACE):
	data=rates(place=place)
	
	newcases={}
	
	_band1,_band2,_band3=0,0,0
	
	for date in sorted(data.keys()):
		
		band1,band2,band3=data[date]

		new_band1=band1-_band1
		new_band2=band2-_band2
		new_band3=band3-_band3
		_all=new_band1+new_band2+new_band3
		newcases[date]=new_band1,new_band2,new_band3,round(new_band1/_all,2)*100,round(new_band2/_all,2)*100,round(new_band3/_all,2)*100
		_band1,_band2,_band3=band1,band2,band3
		
	return newcases	
	
def series(place=PLACE):
	data=new_cases(place=place)
	
	labels,series1,series2,series3,series4,series5,series6=[],[],[],[],[],[],[]
	for date in sorted(data.keys()):
		band1,band2,band3,P1,P2,P3=data[date]
		labels.append(date)
		series1.append(band1)
		series2.append(band2)
		series3.append(band3)
		series4.append(P1)
		series5.append(P2)
		series6.append(P3)
		
		
	return labels,series1,series2,series3,series4,series5,series6
	
	
				

#	_all={}
#	for _range in AGE_RANGES:
#		for _sex in ['_MALE','_FEMALE']:
#			x1=data.get(_range+_sex)
#			_all[_range+_sex] = [x[0] for x in sorted(x1, key=take_second)]
#	


# take the second element for sort
def take_second(elem):
    return elem[1]


def plot(place=PLACE):
	font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 14,
        }
	labels,series1,series2,series3,series4,series5,series6=series()
	plt.plot(series4, 'r', label=LABEL1) # plotting t, a separately 
	plt.plot(series5, 'b', label=LABEL2) # plotting t, a separately 
	plt.plot(series6, 'g', label=LABEL3) # plotting t, a separately 
	plt.legend(title='Cases in '+place)
	plt.title(place+' age distribution of new cases', fontdict=font)
	plt.xlabel('Days since Feb 11,2020', fontdict=font)
	plt.ylabel('% daily new cases', fontdict=font)
	plt.show()