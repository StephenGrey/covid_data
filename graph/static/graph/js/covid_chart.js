
function parse_data(dataset)
{
    		var chart_title="COVID-19 weekly deaths and cases in "+dataset.placename;
    		var date_labels=dataset.week_date_labels;
    		var excess=dataset.excess;
    		var infectlabel=dataset.infectlabel;
    		var caseslabel=dataset.caseslabel;
    		var deathslabel=dataset.deathslabel;
    		var series1=dataset[1].data;
    		var label1=dataset[1].label;

    		var series2=dataset[2].data;
    		var label2=dataset[2].label;

    		var series3=dataset[3].data;
    		var label3=dataset[3].label;

    		var series4=dataset[4].data;
    		var label4=dataset[4].label;

    		var series5=dataset[5].data;
    		var label5=dataset[5].label;
    		
    		var series6=dataset[6].data;
    		var label6=dataset[6].label;
    		
    		var series7=dataset[7].data;
    		var label7=dataset[7].label;
    		
    		var series8=dataset[8].data;
    		var label8=dataset[8].label;

    		var series9=dataset[9].data;
    		var label9=dataset[9].label;

    		var series10=dataset[10].data;
    		var label10=dataset[10].label;

    		var series11=dataset[11].data;
    		var label11=dataset[11].label;
    		var series12=dataset[12].data;
    		var label12=dataset[12].label;

    		var series13=dataset[13].data;
    		var label13=dataset[13].label;
    		var labelseries=dataset[9].labelset;

    		
            ;
            ;
            draw_chart(chart_title,date_labels,excess,infectlabel,caseslabel,deathslabel,series1,series2,series3,series4,series5,series6,series7,series8,series9,series10,series11,series12,series13,label1,label2,label3,label4,label5,label6,label7,label8,label9,label10,label11,label12,label13,labelseries);

};

var api_url="/graph/api/"

function selectOption(sel, val) {
    var opt; 
console.log(sel,val);
    // loop through options in select list
    try
        {
    for ( var i = 0, len = sel.options.length; i < len; i++ ) {

        opt = sel.options[i]; //

        if ( opt.value === val ) {
            opt.selected = true;
            break;
        }
    }

    }
           catch(err) {
    		console.log(err);
    				};
    
}




function get_data(placename)
    {
    console.log('getting data from '+placename);
    if (api_fetch="true")
    {
    	$.get( api_url+placename, function( data ) 
      {
	    console.log('fetched from API');
	    console.log(data);
	    var nation=data.nation
    	var nation_index=data.nation_index
    	var areacode=data.areacode
	    var dataset=data.dataset
	    //console.log(dataset);
	    if (dataset){
	    		//alert(data.results.progress);
     	    parse_data(dataset);
     	    
     	    if (nat_code!=nation_index)
     	    {
     	    console.log('Switch nation');
     	    var sel2 = document.getElementById("Filter2");
            selectOption(sel2,nation_index.toString());
            updateNation();
     	    };
     	    var sel = document.getElementById("Filter"+nation);
            selectOption(sel,placename);
     	};
       });
     }
    else
    {
    var dataset=all_data[placename];
    if (dataset){
    		
    console.log(dataset)//alert(data.results.progress);
    parse_data(dataset);
    
    
    
    		};
     };
    console.log('getting data for '+placename);
     };

function draw_chart(chart_title,date_labels,excess,infectlabel,caseslabel,deathslabel,series1,series2,series3,series4,series5,series6,series7,series8,series9,series10,series11,series12,series13,label1,label2,label3,label4,label5,label6,label7,label8,label9,label10,label11,label12,label13,labelseries)
	{
	params=
	{
    	type: 'line',
    	data: {
        	labels: date_labels,
//        	[
//			'Feb 7','Feb 14','Feb 21','Feb 28','Mar 6','Mar 13','Mar 20', 'Mar 27','Apr 3','Apr 10','Apr 17','Apr 24','May 1','May 8','May 15','May 22','May 29','June 5', 'June 12','June 19','June 26','Jul 3','Jul 10', 'Jul 17', 'Jul 24','Jul 31','Aug 7','Aug 14','Aug 21','Aug 28','Sep 4','Sep 11','Sep 18','Sep 25','Oct 2','Oct 9','Oct 16','Oct 23','Oct 30','Nov 6','Nov 13'],
        	datasets: [
    			
    			{
            	label: label3,
            	data:series3,
            	pointRadius: dots,
            	borderColor: [ 
            	'orange',
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 

    			
    			{
            	label: label4,
            	data: series4,
            	pointRadius: dots,
            	backgroundColor: ['rgba(255,0,0,1)'],
            	borderColor: [ 	'rgba(255, 99, 132, 1)'],
            	borderWidth: 1,    
    			yAxisID: "y-axis-1",
    			
        		},   			
    			{
    			label:label2,
    			data:series2,
    			pointRadius: dots,
            	backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                           	],
            	borderColor: [ 'rgba(255, 99, 132, 1)'
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 


        ]},
        options: {
        	  responsive: true,
    		maintainAspectRatio: false,
    		title: 
    			{
    			display:true,
    			text:chart_title,
    			fontSize: 17,
                
    		 	},
        	tooltips: {
                    callback: function(tooltipItem) {
                        return tooltipItem.yLabel;
                    }
                },
        	
        	
        	scales: 
        		{
            	xAxes: [{
   				    ticks: {
     				   autoSkip: true,
				        maxTicksLimit: 10
  						  }
					}],
            	
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'Weekly Covid+ Deaths and Cases',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
//                    {
                   ],
        		}
    		} //end of options
    	};
	myChart.destroy();
	myChart = new Chart(ctx, params);
	
	//DRAW THE SECOND CHART
	params=
	{
    	type: 'line',
    	data: {
        	labels: date_labels,
        	datasets: [

    			{
    			label:label5,
    			data:series5,
    			pointRadius: dots,
            	borderColor: [ 'rgba(255, 99, 132, 1)'
            	],
            	backgroundColor: ['rgba(255,0,0,0.1)'],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 
    			
    			
    			{
            	label: label7,
            	pointRadius: dots,
            	data: series7,
            	borderColor: [ 'blue'	
            	//'rgba(255, 99, 132, 1)'
            	],
            	borderWidth: 1,    
    			yAxisID: "y-axis-1",
    			
        		},   			
    			{
            	label: label6,
            	pointRadius: dots,
            	data:series6,
            	backgroundColor: ['rgba(255,128,0,0.3)'],
            	borderColor: [ 
            	'rgba(255,0,0,1)'
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 

    			    			{
    			label:label8,
    			pointRadius: dots,
    			data:series8,
				backgroundColor: ['rgba(255,178,102,0.7)'],
            	borderColor: [ 'blue'
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 

        ]},
        options: {
        	  responsive: true,
    		maintainAspectRatio: false,
    		title: 
    			{
    			display:true,
    			text:excess,
    			fontSize: 20,
                
    		 	},
        	scales: 
        		{
        		xAxes: [{
   				    ticks: {
     				   autoSkip: true,
				        maxTicksLimit: 10
  						  }
					}],
     
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'Excess deaths',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
                   ]
                }
                       
    		} //end of options
    	};
	//console.log(params);
	myNewChart.destroy();
	myNewChart = new Chart(new_ctx, params);
	
		//DRAW THE THIRD CHART
	params3=
	{
    	type: 'line',
    	data: {
        	labels: date_labels,
        	datasets: [
    			{
    			label:label1,
    			data:series1,
    			pointRadius: dots,
            	borderColor: [ 'rgba(255, 99, 132, 1)'
            	],
            	backgroundColor: ['rgba(255,0,0,0.1)'],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 
    			
    			
    			{
            	label: label3,
            	pointRadius: dots,
            	data: series3,
            	borderColor: [ 'blue'	
            	//'rgba(255, 99, 132, 1)'
            	],
            	borderWidth: 1,    
    			yAxisID: "y-axis-1",
    			
        		},   			

    			

        ]},
        options: {
        	  responsive: true,
    		maintainAspectRatio: false,
    		title: 
    			{
    			display:true,
    			text:infectlabel,
    			fontSize: 20,
                
    		 	},
        	scales: 
        		{
        		xAxes: [{
   				    ticks: {
     				   autoSkip: true,
				        maxTicksLimit: 10
  						  }
					}],
     
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'Weekly New Cases',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
//                    {
 	
//                   }
                   ]
                }
                       
                        
    		} //end of options
    	};
	//console.log(params);
	Chart3.destroy();
	Chart3 = new Chart(ctx3, params3);
	
	params4=
	{
    	type: 'bar',
    	data: {
        	labels: labelseries,
        	datasets: [
    			{
    			label:label9,
    			data:series9,
            	fillColor: ['blue'],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 
    			{
    			label:label12,
    			data:series12,
    			type: 'line',
    			backgroundColor: ['orange'],
    			borderColor: ['orange'],
    			pointRadius: 0,
            	borderWidth: 3 ,
            	fill: false,
     			yAxisID: "y-axis-1",
     			hidden: false,
    			}, 
    			    			
        		]},
        options: {
        	        	  responsive: true,
    		maintainAspectRatio: false,
    		title: 
    			{
    			display:true,
    			text:caseslabel,
    			fontSize: 20,
                
    		 	},
        	scales: 
        		{
        		xAxes: [{
   				    ticks: {
     				   autoSkip: true,
				        maxTicksLimit: 10
  						  }
					}],
     
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'New Cases (+test by specimen date)',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
//                    {
 	
//                   }
                  ] 
                }
                       
                        
    		} //end of options
    	};	
	

	Chart4.destroy();
	Chart4 = new Chart(ctx4, params4);

	params5=
	{
    	type: 'bar',
    	data: {
        	labels: labelseries,
        	datasets: [
    			{
    			label:label10,
    			data:series10,
            	fillColor: 'pink',
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1",
    			}, 
    			{
    			label:label11,
    			data:series11,
            	backgroundColor: 'red',
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1",
     			hidden: true,
    			}, 
    			{
    			label:label13,
    			data:series13,
    			type: 'line',
            	borderColor: 'orange',
            	pointRadius: 0,
            	borderWidth: 3 ,
            	fill: false,
     			yAxisID: "y-axis-1",
     			hidden: false,
    			}, 

    			
    			
    			]},
        options: {
        //	backgroundColor: ['red'],
        	
        	responsive: true,
    		maintainAspectRatio: false,
    		title: 
    			{
    			display:true,
    			text:deathslabel,
    			fontSize: 20,
                
    		 	},
        	scales: 
        		{
        		xAxes: [{
   				    ticks: {
     				   autoSkip: true,
				        maxTicksLimit: 10
  						  }
					}],
     
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        ticks:{
                        	precision:0
                        	},
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'New Deaths (within 28 days of +ve test)',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
//                    {
 	
//                   }
                  ] 
                }
                       
                        
    		} //end of options
    	};	
	


	Chart5.destroy();
	Chart5 = new Chart(ctx5, params5);

		};



function updateChart() {
    _width=screen.width;
    console.log(_width);
     if (nat_code==1)
     	{
     var determineChart = $("#FilterEngland").val();
 		}
 	else if (nat_code==2)
 		{
     	var determineChart = $("#FilterWales").val();
 		}
 	else if (nat_code==3)
 		{
 		var determineChart = $("#FilterScotland").val();
 		}
 	else {
		var determineChart = $("#FilterNorthern").val();
		};

     console.log('getting data here');
     focus_place=determineChart
     get_data(focus_place);
     zoom2place(focus_place);
 };

function adjustFilter(place){


	
};


function updateNation() {
	var nation_select=$("#Filter2").val();
	//console.log(nation_select);
	nat_code=nation_select;
	if (nation_select=='1'){
		console.log('England');
		$('#FilterEngland').show();
		$('#FilterNorthern').hide();
		$('#FilterScotland').hide();		
		$('#FilterWales').hide();
	}
	else if (nation_select=='2')
	{
		console.log('Wales');
		$('#FilterEngland').hide();
		$('#FilterNorthern').hide();
		$('#FilterScotland').hide();		
		$('#FilterWales').show();
	}
	else if (nation_select=='3'){
		console.log('Scotland');
		$('#FilterEngland').hide();
		$('#FilterNorthern').hide();
		$('#FilterScotland').show();		
		$('#FilterWales').hide();
		}
	else {
		console.log('NI');
		$('#FilterEngland').hide();
		$('#FilterNorthern').show();
		$('#FilterScotland').hide();		
		$('#FilterWales').hide();
		};
	new_nation=nations[nation_select];
	console.log(new_nation);
//	all_data=new_data[new_nation];
	updateChart();
 };



//var all_data= new_data['England'];
var nations={"1": "England", "2":"Wales", "3": "Scotland", "4": "Northern Ireland"};
var currentChart;
var nat_code=1;
var place='Birmingham';
var new_ctx;
var ctx;
var myChart;
var myNewChart;
var dots

document.addEventListener('DOMContentLoaded', (event) => {
  //the event occurred

if (screen.width<600){dots=0} else {dots=2};

ctx = document.getElementById('myChart');
ctx.height = 90;
new_ctx = document.getElementById('myDeathChart');
new_ctx.height = 80;
ctx3 = document.getElementById('estimates');
ctx3.height = 80;
ctx4 = document.getElementById('casechart');
ctx4.height = 80;
ctx5 = document.getElementById('latest_deaths_chart');
ctx5.height = 40;

myChart=new Chart(ctx, {});
myNewChart=new Chart(new_ctx, {});
Chart3=new Chart(ctx3, {});
Chart4=new Chart(ctx4, {});
Chart5=new Chart(ctx5, {});
console.log('charts created')

//FIRST LOAD
$('#FilterEngland').show();
$('#FilterNorthern').hide();
$('#FilterScotland').hide();		
$('#FilterWales').hide();

//WATCHERS
$('#FilterEngland').on('change', updateChart);
$('#FilterNorthern').on('change', updateChart);
$('#FilterWales').on('change', updateChart);
$('#FilterScotland').on('change', updateChart);
$('#Filter2').on('change', updateNation);
$('#FilterData').on('change', updateData);

//updateNation();

})
