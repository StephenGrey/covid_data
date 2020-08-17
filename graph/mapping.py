import json,os
from django.contrib.staticfiles import finders


SCOTLANDMAP_PATH='graph/json/Scotsimplified.json'

print(SCOTLANDMAP_PATH)

def convert_scotland():
    map_path = finders.find(SCOTLANDMAP_PATH)
    assert os.path.exists(map_path)
    folder=os.path.dirname(map_path)
    
    with open(map_path) as json_file:
        mapdata = json.load(json_file)
        
    print(mapdata['objects'].keys())
    geo=mapdata['objects']['Scotsimplified']['geometries']
    newgeo=[]
    for x in geo:
        name=x['properties'].pop('HBName')
        areacode=x['properties'].pop('HBCode')
        
        print(name,areacode)
        x['properties']['lad16nm']=name
        x['properties']['lad16cd']=areacode
        print(x)
        newgeo.append(x)
    mapdata['objects']['Scotsimplified']['geometries']=newgeo
    
    new_map_path=os.path.join(folder,'ScotMap.json')
    with open(new_map_path, 'w') as outfile:
        json.dump(mapdata, outfile)

convert_scotland()

