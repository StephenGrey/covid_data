//https://data.gov.uk/dataset/daaafdcc-f7c7-41ff-80eb-b0b15efd1414/local-authority-districts-december-2017-generalised-clipped-boundaries-in-united-kingdom-wgs84
//Adapted from https://bl.ocks.org/kierandriscoll/93f75337ee73d89e764378cd2d3cc0dd
//
/*
WORKFLOW FOR IMPORTING MAP SHAPES:
Shape file from UK official sources:
http://sedsh127.sedsh.gov.uk/Atom_data/ScotGov/ZippedShapefiles/SG_NHS_HealthBoards_2019.zip


Load UK local authorities and Scottish health districts into QGIS
Delete districts in Buckinghamsire; cut and paste shape of Bucks
Delete Scottish local authorities; load Scottish health districts
Rename columns (field attributes)  to areaname, areacode (so as to match) - using 'Processing Toolbox - Refactor Fields'
Reduce size of file with simplify - Vector - Geometry Tools - Simplify (applying 0.001 degrees)
Save as GeoJson - with options - add Bounding Box
Import into mapshaper and then save as TopoJson  https://mapshaper.org/  
Put file in graph/static/graph/json/ folder
Adjust shape_url variable in line elow for new file name.
*/
   var display_value='cases_rate'
   var shape_url = "/static/graph/json/UK_corrected_topo.json"
//document.getElementById("shape_location").value;
   var map_data_url="/graph/api_rates"
   var legend_values={
	'cases_rate':   [0,5,10,20,40,50],
	'excess_death':[0,40,70,90,110, 130],
};

   var display_value, stat_name, legend0,legend1,legend2, legend3,legend4,legend5,colour_scheme,highlighted_feature
   loadcolour_scheme()

   var map;
   var zoomplace;
   var topoLayer;
   var colourmatrix = {
                    R2G:["#238b45","#74c476","#c7e9c0","#ffcccc","#ff6666","#CC0000",]
                    ,Green:["#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#005a32"]
                    ,Purple: ['#dadaeb','#bcbddc','#9e9ac8','#807dba','#6a51a3','#4a1486']
                    ,Red: ["#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#99000d"]
                    ,Blue:["white", "#6baed6", "#4292c6", "#2171b5", "#085192", "#08306b"]
                    ,Orange:["#fdd0a2", "#fdae6b", "#fd8d3c", "#f16913", "#d94801", "#8c2d04"]
                    }
var highlight = {
    'color': 'red',
    'weight': 6,
    'opacity': 1
};

var unhighlight=
{'color': 'black',
'weight':0.5,
 'opacity': 1 };

//var lagb = "https://raw.githubusercontent.com/kierandriscoll/UK-Topojson/master/Local-Authorities/Local_Auths_Dec16_Gen_Clip_GB.json"
//    var shape_url = "/static/graph/json/Local_Auths_Dec16_Gen_Clip_UK.json"

    var layers = {};
    var references={};
    var startplace="Birmingham";
    var mapLookup;

var legend_map={}
legend_map['cases_rate'] = L.control({position: 'bottomright'});
legend_map['excess_death'] = L.control({position: 'bottomright'});

legend_map['cases_rate'].onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
        grades = [legend0,legend1,legend2,legend3, legend4,legend5],
        labels = ['Cases last 7 days <p>per 100,000 people'];

    // loop through our density intervals and generate a label with a colored square for each interval
    div.innerHTML += labels.join('<br>');
    div.innerHTML += '<br>';
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }
    
    return div;
};
legend_map['excess_death'].onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
        grades = [legend0, legend1, legend2, legend3, legend4,legend5],
        labels = ['Excess deaths'];

    // loop through our density intervals and generate a label with a colored square for each interval
    div.innerHTML += labels.join('<br>');
    div.innerHTML += '<br>';
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }
    
    return div;
};

function loadcolour_scheme(){
   var legends=legend_values[display_value];
   console.log(legends);
   legend0 = legends[0], legend1 = legends[1], legend2=legends[2], legend3=legends[3], legend4=legends[4], legend5=legends[5]; // Must be 6 ranges
   highlighted_feature =null	
   if (display_value=='cases_rate'){
   console.log(legends);
   stat_name = 'Covid-19 cases last 7 days';           // This will be displayed on the map 
   colour_scheme = 'R2G';                             // Either: 'Purple', 'Red', Blue, 'Green', 'Orange', 'R2G'
	}
	else{
    stat_name = 'Excess deaths per 100,000 people';     // This will be displayed on the map 
    colour_scheme = 'Red';                             // Either: 'Purple', 'Red', Blue, 'Green', 'Orange', 'R2G'
	}	
};



function loadmap(place){
	   
console.log('Load map for '+place)
zoomplace=place
   // Local Authority Boundaries data source
 //  var lagb = '{% static 'graph/json/Local_Auths_Dec16_Gen_Clip_GB.json' %}';
 
   var fmtn = d3.format(",.0f"); // Formats all numbers with commas and 0dp
   var fmtph = d3.format(".1%");  // Formats percentages with % and 1dp (only for hover)
   var fmtpl = d3.format(".0%");  // Formats percentages with % and 0dp (only for legend)
 
  
  // initialize Leaflet
map =  new L.Map('mapid', { center: new L.LatLng(53.10, -1.26),zoom: 7   });
//L.map('mapid').setView([51.505, -0.09], 13);

var layer = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

 layer.addTo(map);
 
//add the default legend to the map
legend_map['cases_rate'].addTo(map);

add_shades();

};

  function add_shades(){
   //Code to convert TopoJson to GeoJson
   L.TopoJSON = L.GeoJSON.extend({ 
                  addData: function(jsonData) {   
                           if (jsonData.type === "Topology") {
                               for (key in jsonData.objects) {
                                    geojson = topojson.feature(jsonData, jsonData.objects[key]);
                                    L.GeoJSON.prototype.addData.call(this, geojson);
    }}   
                           else {
                                    L.GeoJSON.prototype.addData.call(this, jsonData);
    }}});
 
  topoLayer = new L.TopoJSON();
  console.log(topoLayer);
//  topoLayer.on('data:loaded',function(e){
//  console.log("loaded");   
//  });
    // Possible Colour Schemes

  // Imports boundary data and passes to the addTopoData function
  mapLookup = d3.map();


d3.json(map_data_url, function (data) {
 //   console.log(data);
    data.dataset.forEach( function(d) {
    	if (display_value=='cases_rate'){
    	mapLookup.set(d.areaname,d.cases_rate);   //+d.excess
    	}else{
    	mapLookup.set(d.areaname,d.excess);
    	};
    	
    	});
    $.getJSON(shape_url).done(addTopoData);
});
  	
  	
  	
  };


// Colours used (uses parameters defined at start)

  function getColor(d) {
    return d == null ? 'grey': 
           d > legend5 ? colourmatrix[colour_scheme][5] :
           d > legend4 ? colourmatrix[colour_scheme][4] :
           d > legend3 ? colourmatrix[colour_scheme][3] :
           d > legend2 ? colourmatrix[colour_scheme][2] :
           d > legend1 ? colourmatrix[colour_scheme][1] :
           d >= legend0 ? colourmatrix[colour_scheme][0] :
                         'grey';
  }
  // Draws the boundary data on the map
function addTopoData(topoData) { 
           topoLayer.addData(topoData);
           topoLayer.addTo(map);
           topoLayer.eachLayer(handleLayer);
           zoom2place(zoomplace);
   }
 
 
// Set the style of the boundary data layer (fill color based on data values)
function handleLayer(layer) {
   //console.log(mapLookup.get(layer.feature.properties.lad16nm));
   layer_value=mapLookup.get(layer.feature.properties.areaname);
   layer.setStyle({ fillColor : getColor(layer_value),
                     fillOpacity: 0.6,
                     color: 'black',
                     weight:0.5,
                     opacity: 1 });
                    
   layer.on({ mouseover : enterLayer,
               mouseout: leaveLayer,
               click: clicklayer,  });
   
   layers[layer._leaflet_id] = layer;
   references[layer.feature.properties.areaname]=layer;
  } //End of handleLayer function

function updateData(){
console.log('update data');
display_value= $("#FilterData").val();
console.log(display_value);
loadcolour_scheme()
map.removeLayer(topoLayer);
add_shades();

if (display_value === 'cases_rate') {
        map.removeControl(legend_map['excess_death']);
        legend_map['cases_rate'].addTo(map);
    } else { // Or switch to the Population Change legend...
        map.removeControl(legend_map['cases_rate']);
        legend_map['excess_death'].addTo(map);
    };
};

function zoom2place(place) {
    console.log('zooming to : '+place);
    
    try {
    var feat = references[place]
    map.fitBounds(feat._bounds)
    highlightLayer(feat);
    window.history.pushState(place,'COVID Kingdom: the UK COVID-19 Tracker','/graph/place='+place);
    
    }
     catch(err) {
    console.log(err);
    };
   };




function loadData(src) {

    d3.json(src, function(error, data) {
        if (error) return console.warn(error);

        layers = {}; // reset reference

        L.geoJSON(data, {
            style: myStyle,
            onEachFeature: eachFeature
        }).addTo(map);

    });
}

function zoomToFeature(e) {
        var feature = L.geoJson(e).addTo(map);
		map.fitBounds(feature.getBounds());
        }

function highlightLayer(layerID) {
	if (highlighted_feature) {
	highlighted_feature.setStyle(unhighlight);
    }
	_this=map._layers[layerID._leaflet_id]
    _this.setStyle(highlight);
    highlighted_feature=_this;
}
 
  // Add Tooltip feature
  var info = L.control();
 
  info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
  };
 
  // Behaviour when mouseover an area
  function enterLayer(){  
       this.setStyle({ weight: 2, opacity: 1 });
       var areaname = this.feature.properties.areaname; // Local Authority Name
       var areaid = this.feature.properties.areacode;   // LA code 
       var excess=mapLookup.get(areaname)
       // method that we will use to update the tooltip feature
       info.update = function () {
         if (display_value=='cases_rate')
            {
            this._div.innerHTML = stat_name + ' <br/> <b>' + areaname + '</b> <br/> '+ excess+ ' cases per 100,000 people';
         }else
        	{
        this._div.innerHTML = stat_name + ' <br/> <b>' + areaname + '</b> <br/> '+ excess+ ' deaths per 100,000 people';
        };
    };
        info.addTo(map); 
  };

  function clicklayer(){
      clickplace= this.feature.properties.areaname;
      console.log('clicked on '+clickplace);
      //zoomToFeature(this.feature);
      zoom2place(clickplace);
      get_data(clickplace);
  };


  // Behaviour when mouseout an area
  function leaveLayer(){
       this.setStyle({ weight: 0.5 });
       // method that we will use to reset the tooltip feature
       info.update = function () {
            this._div.innerHTML = 'Hover over an area for more information';
       };
       info.addTo(map);
  }; 

