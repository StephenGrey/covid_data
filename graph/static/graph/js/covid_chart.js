
function parse_data(dataset)
{
    		var chart_title=dataset.placename;
    		var excess=dataset.excess;
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

            ;
            draw_chart(chart_title,excess,series1,series2,series3,series4,series5,series6,series7,series8,label1,label2,label3,label4,label5,label6,label7,label8);

};

var api_url="/graph/api/"

function get_data(placename)
    {
    if (api_fetch="true")
    {
    	$.get( api_url+placename, function( data ) 
      {
	    var dataset=data.dataset
	    //console.log(dataset);
	    if (dataset){
	    		//alert(data.results.progress);
     	    parse_data(dataset);
     	         	};
       });
     }
    else
    {
    var dataset=all_data[placename];
    if (dataset){
    		
    		//console.log(dataset)//alert(data.results.progress);
    parse_data(dataset);

    		};
     };
     };

function draw_chart(chart_title,excess,series1,series2,series3,series4,series5,series6,series7,series8,label1,label2,label3,label4,label5,label6,label7,label8)
	{
	params=
	{
    	type: 'line',
    	data: {
        	labels: [
			'Feb 7','Feb 14','Feb 21','Feb 28','Mar 6','Mar 13','Mar 20', 'Mar 27','Apr 3','Apr 10','Apr 17','Apr 24','May 1','May 8','May 15','May 22','May 29','June 5', 'June 12','June 19','June 26','Jul 3','Jul 10', 'Jul 17', 'Jul 24'],
        	datasets: [
        		{
            		label: label1,
            		data: series1,
            		borderDash: [10,5],
            		backgroundColor: [
					'rgba(255, 229, 204,0.4)',
            		],
            		borderColor: [
            		'black'
],
            		borderWidth: 1,
             		yAxisID: "y-axis-1",
             		
    			}, 
    			
    			
    			{
            	label: label3,
            	data:series3,
            	borderColor: [ 
            	'orange',
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-2"
    			}, 

    			
    			{
            	label: label4,
            	data: series4,
            	backgroundColor: ['rgba(255,0,0,1)'],
            	borderColor: [ 	'rgba(255, 99, 132, 1)'],
            	borderWidth: 1,    
    			yAxisID: "y-axis-2",
    			
        		},   			
    			{
    			label:label2,
    			data:series2,
            	backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                           	],
            	borderColor: [ 'rgba(255, 99, 132, 1)'
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-2"
    			}, 


        ]},
        options: {
    		title: 
    			{
    			display:true,
    			text:chart_title,
    			fontSize: 17,
                
    		 	},
        	scales: 
        		{
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'Weekly New Infections',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
                    {
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "right",
                        scaleLabel: {
                            display: true,
                            labelString: 'Deaths / COVID-Positive Cases',
                            fontColor: "red",
      								},
                        id: "y-axis-2",
                        
                        // grid line settings
                        gridLines: {
                            drawOnChartArea: false, // only want the grid lines for one axis to show up
                        	},
                   }],
        		}
    		} //end of options
    	};
	//console.log(params);
	myChart.destroy();
	myChart = new Chart(ctx, params);
	
	//DRAW THE SECOND CHART
	params=
	{
    	type: 'line',
    	data: {
        	labels: [
			'Feb 7','Feb 14','Feb 21', 'Feb 28','Mar 6','Mar 13','Mar 20', 'Mar 27','Apr 3','Apr 10', 'Apr 17','Apr 24','May 1','May 8','May 15','May 22','May 29','June 5', 'June 12','June 19','June 26','Jul 3','Jul 10', 'Jul 17', 'Jul 24'],
        	datasets: [
//        		{
//            		label: label1,
//            		data: series1,
//            		borderDash: [10,5],
//            		borderColor: [
//            		'black'
//					],
//            		borderWidth: 1,
//             		yAxisID: "y-axis-1",
//             		
//    			}, 

    			{
    			label:label5,
    			data:series5,
            	borderColor: [ 'rgba(255, 99, 132, 1)'
            	],
            	backgroundColor: ['rgba(255,0,0,0.1)'],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 
    			
    			

    			
    			{
            	label: label7,
            	data: series7,
            	borderColor: [ 'blue'	
            	//'rgba(255, 99, 132, 1)'
            	],
            	borderWidth: 1,    
    			yAxisID: "y-axis-1",
    			
        		},   			
    			{
            	label: label6,
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
    			data:series8,
				backgroundColor: ['rgba(255,178,102,0.7)'],
            	borderColor: [ 'blue'
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, 
/*    			    			{
    			label:label6,
    			data:series6,
            	backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                           	],
            	borderColor: [ 'rgba(255, 99, 132, 1)'
            	],
            	borderWidth: 1 ,
     			yAxisID: "y-axis-1"
    			}, */
    			

        ]},
        options: {
    		title: 
    			{
    			display:true,
    			text:excess,
    			fontSize: 12,
                
    		 	},
        	scales: 
        		{
            	yAxes: 
            		[{            
                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                        display: true,
                        position: "left",
                        scaleLabel: 
                        	{
                            display: true,
                            labelString: 'Weekly Deaths',
                            fontColor: "black",
                        	},
                        id: "y-axis-1",
                    }, 
//                    {
//                        type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
//                        display: true,
//                        position: "right",
//                        ticks: {
//                         beginAtZero: true,
//                          max: 45,
//                          min: 0,
//                          stepSize: 5
//                          },
//                        //scaleLabel: {
//                        //    display: true,
//                        //    labelString: '',
//                        //    fontColor: "red",
//      					//			},
//      					
//                         id: "y-axis-2",
//                        // grid line settings
//                    gridLines: {
//                            drawOnChartArea: false, // only want the grid lines for one axis to show up
//                        	},
//                   }
                   ]
                }
                       
                        
    		} //end of options
    	};
	//console.log(params);
	myNewChart.destroy();
	myNewChart = new Chart(new_ctx, params);
		};


function updateChart() {

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
		var determineChart = $("#FilterNI").val();
		};

     //console.log(determineChart);
     get_data(determineChart);
 };


function updateNation() {
	var nation_select=$("#Filter2").val();
	//console.log(nation_select);
	nat_code=nation_select;
	if (nation_select=='1'){
		console.log('England');
		$('#FilterEngland').show();
		$('#FilterNI').hide();
		$('#FilterScotland').hide();		
		$('#FilterWales').hide();
	}
	else if (nation_select=='2')
	{
		console.log('Wales');
		$('#FilterEngland').hide();
		$('#FilterNI').hide();
		$('#FilterScotland').hide();		
		$('#FilterWales').show();
	}
	else if (nation_select=='3'){
		console.log('Scotland');
		$('#FilterEngland').hide();
		$('#FilterNI').hide();
		$('#FilterScotland').show();		
		$('#FilterWales').hide();
		}
	else {
		console.log('NI');
		$('#FilterEngland').hide();
		$('#FilterNI').show();
		$('#FilterScotland').hide();		
		$('#FilterWales').hide();
		};
	new_nation=nations[nation_select];
	all_data=new_data[new_nation];
	updateChart();
 };

var all_data= new_data['England'];
var nations={"1": "England", "2":"Wales", "3": "Scotland", "4": "Northern Ireland"};
var currentChart;
var nat_code=1
var place='Birmingham'
var ctx = document.getElementById('myChart');
ctx.height = 80;
var new_ctx = document.getElementById('myDeathChart');
new_ctx.height = 50;

var myChart;
var myNewChart;

myChart=new Chart(ctx, {});
myNewChart=new Chart(new_ctx, {});


//FIRST LOAD
$('#FilterEngland').show();
$('#FilterNI').hide();
$('#FilterScotland').hide();		
$('#FilterWales').hide();

//WATCHERS
$('#FilterEngland').on('change', updateChart);
$('#FilterNI').on('change', updateChart);
$('#FilterWales').on('change', updateChart);
$('#FilterScotland').on('change', updateChart);
$('#Filter2').on('change', updateNation);

updateNation();

