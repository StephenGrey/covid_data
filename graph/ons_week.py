from datetime import datetime,timedelta
import pytz

weeks={1:(3,1,2020),2:(10,1,2020),3:(17,1,2020),4:(24,1,2020),5:(31,1,2020),6:(7,2,2020),7:(14,2,2020),8:(21,2,2020),9:(28,2,2020),10:(6,3,2020),11:(13,3,2020),12:(20,3,2020),13:(27,3,2020),14:(3,4,2020),15:(10,4,2020),16:(17,4,2020),17:(24,4,2020),18:(1,5,2020),19:(8,5,2020),20:(15,5,2020),21:(22,5,2020),22:(29,5,2020),23:(5,6,2020),24:(12,6,2020),25:(19,6,2020),26:(26,6,2020),27:(3,7,2020),28:(10,7,2020),29:(17,7,2020),30:(24,7,2020),31:(31,7,2020),32:(7,8,2020),33:(14,8,2020),34:(21,8,2020),35:(28,8,2020),36:(4,9,2020),37:(11,9,2020),38:(18,9,2020),39:(25,9,2020),40:(2,10,2020),41:(9,10,2020),42:(16,10,2020),43:(23,10,2020),44:(30,10,2020),45:(6,11,2020),46:(13,11,2020),47:(20,11,2020),48:(27,11,2020),49:(4,12,2020),50:(11,12,2020),51:(18,12,2020),52:(25,12,2020),53:(1,1,2021)}

names={'E09000001':'City of London','E06000060':'Buckinghamshire','E09000033': 'Westminster', 'E09000032': 'Wandsworth', 
	'E09000031': 'Waltham Forest', 'E09000030': 'Tower Hamlets', 'E09000029': 'Sutton', 'E09000028': 'Southwark', 'E09000027': 'Richmond upon Thames', 'E09000026': 'Redbridge', 'E09000025': 'Newham', 'E09000024': 'Merton', 'E09000023': 'Lewisham', 'E09000022': 'Lambeth', 'E09000021': 'Kingston upon Thames', 'E09000020': 'Kensington and Chelsea', 'E09000019': 'Islington', 'E09000018': 'Hounslow', 'E09000017': 'Hillingdon', 'E09000016': 'Havering', 'E09000015': 'Harrow', 'E09000014': 'Haringey', 'E09000013': 'Hammersmith and Fulham', 'E09000012': 'Hackney and City of London', 'E09000011': 'Greenwich', 'E09000010': 'Enfield', 'E09000009': 'Ealing', 'E09000008': 'Croydon', 'E09000007': 'Camden', 'E09000006': 'Bromley', 'E09000005': 'Brent', 'E09000004': 'Bexley', 'E09000003': 'Barnet', 'E09000002': 'Barking and Dagenham', 'E08000037': 'Gateshead', 'E08000036': 'Wakefield', 'E08000035': 'Leeds', 'E08000034': 'Kirklees', 'E08000033': 'Calderdale', 'E08000032': 'Bradford', 'E08000031': 'Wolverhampton', 'E08000030': 'Walsall', 'E08000029': 'Solihull', 'E08000028': 'Sandwell', 'E08000027': 'Dudley', 'E08000026': 'Coventry', 'E08000025': 'Birmingham', 'E08000024': 'Sunderland', 'E08000023': 'South Tyneside', 'E08000022': 'North Tyneside', 'E08000021': 'Newcastle upon Tyne', 'E08000019': 'Sheffield', 'E08000018': 'Rotherham', 'E08000017': 'Doncaster', 'E08000016': 'Barnsley', 'E08000015': 'Wirral', 'E08000014': 'Sefton', 'E08000013': 'St. Helens', 'E08000012': 'Liverpool', 'E08000011': 'Knowsley', 'E08000010': 'Wigan', 'E08000009': 'Trafford', 'E08000008': 'Tameside', 'E08000007': 'Stockport', 'E08000006': 'Salford', 'E08000005': 'Rochdale', 'E08000004': 'Oldham', 'E08000003': 'Manchester', 'E08000002': 'Bury', 'E08000001': 'Bolton', 'E07000246': 'Somerset West and Taunton', 'E07000245': 'West Suffolk', 'E07000244': 'East Suffolk', 'E07000243': 'Stevenage', 'E07000242': 'East Hertfordshire', 'E07000241': 'Welwyn Hatfield', 'E07000240': 'St Albans', 'E07000239': 'Wyre Forest', 'E07000238': 'Wychavon', 'E07000237': 'Worcester', 'E07000236': 'Redditch', 'E07000235': 'Malvern Hills', 'E07000234': 'Bromsgrove', 'E07000229': 'Worthing', 'E07000228': 'Mid Sussex', 'E07000227': 'Horsham', 'E07000226': 'Crawley', 'E07000225': 'Chichester', 'E07000224': 'Arun', 'E07000223': 'Adur', 'E07000222': 'Warwick', 'E07000221': 'Stratford-on-Avon', 'E07000220': 'Rugby', 'E07000219': 'Nuneaton and Bedworth', 'E07000218': 'North Warwickshire', 'E07000217': 'Woking', 'E07000216': 'Waverley', 'E07000215': 'Tandridge', 'E07000214': 'Surrey Heath', 'E07000213': 'Spelthorne', 'E07000212': 'Runnymede', 'E07000211': 'Reigate and Banstead', 'E07000210': 'Mole Valley', 'E07000209': 'Guildford', 'E07000208': 'Epsom and Ewell', 'E07000207': 'Elmbridge', 'E07000203': 'Mid Suffolk', 'E07000202': 'Ipswich', 'E07000200': 'Babergh', 'E07000199': 'Tamworth', 'E07000198': 'Staffordshire Moorlands', 'E07000197': 'Stafford', 'E07000196': 'South Staffordshire', 'E07000195': 'Newcastle-under-Lyme', 'E07000194': 'Lichfield', 'E07000193': 'East Staffordshire', 'E07000192': 'Cannock Chase', 'E07000189': 'South Somerset', 'E07000188': 'Sedgemoor', 'E07000187': 'Mendip', 'E07000181': 'West Oxfordshire', 'E07000180': 'Vale of White Horse', 'E07000179': 'South Oxfordshire', 'E07000178': 'Oxford', 'E07000177': 'Cherwell', 'E07000176': 'Rushcliffe', 'E07000175': 'Newark and Sherwood', 'E07000174': 'Mansfield', 'E07000173': 'Gedling', 'E07000172': 'Broxtowe', 'E07000171': 'Bassetlaw', 'E07000170': 'Ashfield', 'E07000169': 'Selby', 'E07000168': 'Scarborough', 'E07000167': 'Ryedale', 'E07000166': 'Richmondshire', 'E07000165': 'Harrogate', 'E07000164': 'Hambleton', 'E07000163': 'Craven', 'E07000156': 'Wellingborough', 'E07000155': 'South Northamptonshire', 'E07000154': 'Northampton', 'E07000153': 'Kettering', 'E07000152': 'East Northamptonshire', 'E07000151': 'Daventry', 'E07000150': 'Corby', 'E07000149': 'South Norfolk', 'E07000148': 'Norwich', 'E07000147': 'North Norfolk', 'E07000146': """King's Lynn and West Norfolk""", 'E07000145': 'Great Yarmouth', 'E07000144': 'Broadland', 'E07000143': 'Breckland', 'E07000142': 'West Lindsey', 'E07000141': 'South Kesteven', 'E07000140': 'South Holland', 'E07000139': 'North Kesteven', 'E07000138': 'Lincoln', 'E07000137': 'East Lindsey', 'E07000136': 'Boston', 'E07000135': 'Oadby and Wigston', 'E07000134': 'North West Leicestershire', 'E07000133': 'Melton', 'E07000132': 'Hinckley and Bosworth', 'E07000131': 'Harborough', 'E07000130': 'Charnwood', 'E07000129': 'Blaby', 'E07000128': 'Wyre', 'E07000127': 'West Lancashire', 'E07000126': 'South Ribble', 'E07000125': 'Rossendale', 'E07000124': 'Ribble Valley', 'E07000123': 'Preston', 'E07000122': 'Pendle', 'E07000121': 'Lancaster', 'E07000120': 'Hyndburn', 'E07000119': 'Fylde', 'E07000118': 'Chorley', 'E07000117': 'Burnley', 'E07000116': 'Tunbridge Wells', 'E07000115': 'Tonbridge and Malling', 'E07000114': 'Thanet', 'E07000113': 'Swale', 'E07000112': 'Folkestone and Hythe', 'E07000111': 'Sevenoaks', 'E07000110': 'Maidstone', 'E07000109': 'Gravesham', 'E07000108': 'Dover', 'E07000107': 'Dartford', 'E07000106': 'Canterbury', 'E07000105': 'Ashford', 'E07000103': 'Watford', 'E07000102': 'Three Rivers', 'E07000099': 'North Hertfordshire', 'E07000098': 'Hertsmere', 'E07000096': 'Dacorum', 'E07000095': 'Broxbourne', 'E07000094': 'Winchester', 'E07000093': 'Test Valley', 'E07000092': 'Rushmoor', 'E07000091': 'New Forest', 'E07000090': 'Havant', 'E07000089': 'Hart', 'E07000088': 'Gosport', 'E07000087': 'Fareham', 'E07000086': 'Eastleigh', 'E07000085': 'East Hampshire', 'E07000084': 'Basingstoke and Deane', 'E07000083': 'Tewkesbury', 'E07000082': 'Stroud', 'E07000081': 'Gloucester', 'E07000080': 'Forest of Dean', 'E07000079': 'Cotswold', 'E07000078': 'Cheltenham', 'E07000077': 'Uttlesford', 'E07000076': 'Tendring', 'E07000075': 'Rochford', 'E07000074': 'Maldon', 'E07000073': 'Harlow', 'E07000072': 'Epping Forest', 'E07000071': 'Colchester', 'E07000070': 'Chelmsford', 'E07000069': 'Castle Point', 'E07000068': 'Brentwood', 'E07000067': 'Braintree', 'E07000066': 'Basildon', 'E07000065': 'Wealden', 'E07000064': 'Rother', 'E07000063': 'Lewes', 'E07000062': 'Hastings', 'E07000061': 'Eastbourne', 'E07000047': 'West Devon', 'E07000046': 'Torridge', 'E07000045': 'Teignbridge', 'E07000044': 'South Hams', 'E07000043': 'North Devon', 'E07000042': 'Mid Devon', 'E07000041': 'Exeter', 'E07000040': 'East Devon', 'E07000039': 'South Derbyshire', 'E07000038': 'North East Derbyshire', 'E07000037': 'High Peak', 'E07000036': 'Erewash', 'E07000035': 'Derbyshire Dales', 'E07000034': 'Chesterfield', 'E07000033': 'Bolsover', 'E07000032': 'Amber Valley', 'E07000031': 'South Lakeland', 'E07000030': 'Eden', 'E07000029': 'Copeland', 'E07000028': 'Carlisle', 'E07000027': 'Barrow-in-Furness', 'E07000026': 'Allerdale', 'E07000012': 'South Cambridgeshire', 'E07000011': 'Huntingdonshire', 'E07000010': 'Fenland', 'E07000009': 'East Cambridgeshire', 'E07000008': 'Cambridge', 'E07000007': 'Wycombe', 'E07000006': 'South Bucks', 'E07000005': 'Chiltern', 'E07000004': 'Aylesbury Vale', 'E06000059': 'Dorset', 'E06000058': 'Bournemouth, Christchurch and Poole', 'E06000057': 'Northumberland', 'E06000056': 'Central Bedfordshire', 'E06000055': 'Bedford', 'E06000054': 'Wiltshire', 'E06000052': 'Cornwall','E37000005':'Cornwall and Isles of Scilly', 'E06000051': 'Shropshire', 'E06000050': 'Cheshire West and Chester', 'E06000049': 'Cheshire East', 'E06000047': 'County Durham', 'E06000046': 'Isle of Wight', 'E06000045': 'Southampton', 'E06000044': 'Portsmouth', 'E06000043': 'Brighton and Hove', 'E06000042': 'Milton Keynes', 'E06000041': 'Wokingham', 'E06000040': 'Windsor and Maidenhead', 'E06000039': 'Slough', 'E06000038': 'Reading', 'E06000037': 'West Berkshire', 'E06000036': 'Bracknell Forest', 'E06000035': 'Medway', 'E06000034': 'Thurrock', 'E06000033': 'Southend-on-Sea', 'E06000032': 'Luton', 'E06000031': 'Peterborough', 'E06000030': 'Swindon', 'E06000027': 'Torbay', 'E06000026': 'Plymouth', 'E06000025': 'South Gloucestershire', 'E06000024': 'North Somerset', 'E06000023': 'Bristol, City of', 'E06000022': 'Bath and North East Somerset', 'E06000021': 'Stoke-on-Trent', 'E06000020': 'Telford and Wrekin', 'E06000019': 'Herefordshire, County of', 'E06000018': 'Nottingham', 'E06000017': 'Rutland', 'E06000016': 'Leicester', 'E06000015': 'Derby', 'E06000014': 'York', 'E06000013': 'North Lincolnshire', 'E06000012': 'North East Lincolnshire', 'E06000011': 'East Riding of Yorkshire', 'E06000010': 'Kingston upon Hull, City of', 'E06000009': 'Blackpool', 'E06000008': 'Blackburn with Darwen', 'E06000007': 'Warrington', 'E06000006': 'Halton', 'E06000005': 'Darlington', 'E06000004': 'Stockton-on-Tees', 'E06000003': 'Redcar and Cleveland', 'E06000002': 'Middlesbrough', 'E06000001': 'Hartlepool', 'E10000034': 'Worcestershire', 'E10000032': 'West Sussex', 'E10000031': 'Warwickshire', 'E10000030': 'Surrey', 'E10000029': 'Suffolk', 'E10000028': 'Staffordshire', 'E10000027': 'Somerset', 'E10000025': 'Oxfordshire', 'E10000024': 'Nottinghamshire', 'E10000023': 'North Yorkshire', 'E10000021': 'Northamptonshire', 'E10000020': 'Norfolk', 'E10000019': 'Lincolnshire', 'E10000018': 'Leicestershire', 'E10000017': 'Lancashire', 'E10000016': 'Kent', 'E10000015': 'Hertfordshire', 'E10000014': 'Hampshire', 'E10000013': 'Gloucestershire', 'E10000012': 'Essex', 'E10000011': 'East Sussex', 'E10000008': 'Devon', 'E10000007': 'Derbyshire', 'E10000006': 'Cumbria', 'E10000003': 'Cambridgeshire', 'E10000002': 'Buckinghamshire', 'E92000001': 'England', 'E12000009': 'South West', 'E12000008': 'South East', 'E12000007': 'London', 'E12000006': 'East of England', 'E12000005': 'West Midlands', 'E12000004': 'East Midlands', 'E12000003': 'Yorkshire and The Humber', 'E12000002': 'North West', 'E12000001': 'North East'}

stored_names={'E06000001': 'Hartlepool', 'E06000002': 'Middlesbrough', 'E06000003': 'Redcar and Cleveland', 'E06000004': 'Stockton-on-Tees', 'E06000005': 'Darlington', 'E06000006': 'Halton', 'E06000007': 'Warrington', 'E06000008': 'Blackburn with Darwen', 'E06000009': 'Blackpool', 'E06000010': 'Kingston upon Hull, City of', 'E06000011': 'East Riding of Yorkshire', 'E06000012': 'North East Lincolnshire', 'E06000013': 'North Lincolnshire', 'E06000014': 'York', 'E06000015': 'Derby', 'E06000016': 'Leicester', 'E06000017': 'Rutland', 'E06000018': 'Nottingham', 'E06000019': 'Herefordshire, County of', 'E06000020': 'Telford and Wrekin', 'E06000021': 'Stoke-on-Trent', 'E06000022': 'Bath and North East Somerset', 'E06000023': 'Bristol, City of', 'E06000024': 'North Somerset', 'E06000025': 'South Gloucestershire', 'E06000026': 'Plymouth', 'E06000027': 'Torbay', 'E06000030': 'Swindon', 'E06000031': 'Peterborough', 'E06000032': 'Luton', 'E06000033': 'Southend-on-Sea', 'E06000034': 'Thurrock', 'E06000035': 'Medway', 'E06000036': 'Bracknell Forest', 'E06000037': 'West Berkshire', 'E06000038': 'Reading', 'E06000039': 'Slough', 'E06000040': 'Windsor and Maidenhead', 'E06000041': 'Wokingham', 'E06000042': 'Milton Keynes', 'E06000043': 'Brighton and Hove', 'E06000044': 'Portsmouth', 'E06000045': 'Southampton', 'E06000046': 'Isle of Wight', 'E06000047': 'County Durham', 'E06000049': 'Cheshire East', 'E06000050': 'Cheshire West and Chester', 'E06000051': 'Shropshire', 'E06000052': 'Cornwall and Isles of Scilly', 'E06000053': 'Isles of Scilly', 'E06000054': 'Wiltshire', 'E06000055': 'Bedford', 'E06000056': 'Central Bedfordshire', 'E06000057': 'Northumberland', 'E06000058': 'Bournemouth, Christchurch and Poole', 'E06000059': 'Dorset', 'E06000060': 'Buckinghamshire', 'E07000008': 'Cambridge', 'E07000009': 'East Cambridgeshire', 'E07000010': 'Fenland', 'E07000011': 'Huntingdonshire', 'E07000012': 'South Cambridgeshire', 'E07000026': 'Allerdale', 'E07000027': 'Barrow-in-Furness', 'E07000028': 'Carlisle', 'E07000029': 'Copeland', 'E07000030': 'Eden', 'E07000031': 'South Lakeland', 'E07000032': 'Amber Valley', 'E07000033': 'Bolsover', 'E07000034': 'Chesterfield', 'E07000035': 'Derbyshire Dales', 'E07000036': 'Erewash', 'E07000037': 'High Peak', 'E07000038': 'North East Derbyshire', 'E07000039': 'South Derbyshire', 'E07000040': 'East Devon', 'E07000041': 'Exeter', 'E07000042': 'Mid Devon', 'E07000043': 'North Devon', 'E07000044': 'South Hams', 'E07000045': 'Teignbridge', 'E07000046': 'Torridge', 'E07000047': 'West Devon', 'E07000061': 'Eastbourne', 'E07000062': 'Hastings', 'E07000063': 'Lewes', 'E07000064': 'Rother', 'E07000065': 'Wealden', 'E07000066': 'Basildon', 'E07000067': 'Braintree', 'E07000068': 'Brentwood', 'E07000069': 'Castle Point', 'E07000070': 'Chelmsford', 'E07000071': 'Colchester', 'E07000072': 'Epping Forest', 'E07000073': 'Harlow', 'E07000074': 'Maldon', 'E07000075': 'Rochford', 'E07000076': 'Tendring', 'E07000077': 'Uttlesford', 'E07000078': 'Cheltenham', 'E07000079': 'Cotswold', 'E07000080': 'Forest of Dean', 'E07000081': 'Gloucester', 'E07000082': 'Stroud', 'E07000083': 'Tewkesbury', 'E07000084': 'Basingstoke and Deane', 'E07000085': 'East Hampshire', 'E07000086': 'Eastleigh', 'E07000087': 'Fareham', 'E07000088': 'Gosport', 'E07000089': 'Hart', 'E07000090': 'Havant', 'E07000091': 'New Forest', 'E07000092': 'Rushmoor', 'E07000093': 'Test Valley', 'E07000094': 'Winchester', 'E07000095': 'Broxbourne', 'E07000096': 'Dacorum', 'E07000098': 'Hertsmere', 'E07000099': 'North Hertfordshire', 'E07000102': 'Three Rivers', 'E07000103': 'Watford', 'E07000105': 'Ashford', 'E07000106': 'Canterbury', 'E07000107': 'Dartford', 'E07000108': 'Dover', 'E07000109': 'Gravesham', 'E07000110': 'Maidstone', 'E07000111': 'Sevenoaks', 'E07000112': 'Folkestone and Hythe', 'E07000113': 'Swale', 'E07000114': 'Thanet', 'E07000115': 'Tonbridge and Malling', 'E07000116': 'Tunbridge Wells', 'E07000117': 'Burnley', 'E07000118': 'Chorley', 'E07000119': 'Fylde', 'E07000120': 'Hyndburn', 'E07000121': 'Lancaster', 'E07000122': 'Pendle', 'E07000123': 'Preston', 'E07000124': 'Ribble Valley', 'E07000125': 'Rossendale', 'E07000126': 'South Ribble', 'E07000127': 'West Lancashire', 'E07000128': 'Wyre', 'E07000129': 'Blaby', 'E07000130': 'Charnwood', 'E07000131': 'Harborough', 'E07000132': 'Hinckley and Bosworth', 'E07000133': 'Melton', 'E07000134': 'North West Leicestershire', 'E07000135': 'Oadby and Wigston', 'E07000136': 'Boston', 'E07000137': 'East Lindsey', 'E07000138': 'Lincoln', 'E07000139': 'North Kesteven', 'E07000140': 'South Holland', 'E07000141': 'South Kesteven', 'E07000142': 'West Lindsey', 'E07000143': 'Breckland', 'E07000144': 'Broadland', 'E07000145': 'Great Yarmouth', 'E07000146': "King's Lynn and West Norfolk", 'E07000147': 'North Norfolk', 'E07000148': 'Norwich', 'E07000149': 'South Norfolk', 'E07000150': 'Corby', 'E07000151': 'Daventry', 'E07000152': 'East Northamptonshire', 'E07000153': 'Kettering', 'E07000154': 'Northampton', 'E07000155': 'South Northamptonshire', 'E07000156': 'Wellingborough', 'E07000163': 'Craven', 'E07000164': 'Hambleton', 'E07000165': 'Harrogate', 'E07000166': 'Richmondshire', 'E07000167': 'Ryedale', 'E07000168': 'Scarborough', 'E07000169': 'Selby', 'E07000170': 'Ashfield', 'E07000171': 'Bassetlaw', 'E07000172': 'Broxtowe', 'E07000173': 'Gedling', 'E07000174': 'Mansfield', 'E07000175': 'Newark and Sherwood', 'E07000176': 'Rushcliffe', 'E07000177': 'Cherwell', 'E07000178': 'Oxford', 'E07000179': 'South Oxfordshire', 'E07000180': 'Vale of White Horse', 'E07000181': 'West Oxfordshire', 'E07000187': 'Mendip', 'E07000188': 'Sedgemoor', 'E07000189': 'South Somerset', 'E07000192': 'Cannock Chase', 'E07000193': 'East Staffordshire', 'E07000194': 'Lichfield', 'E07000195': 'Newcastle-under-Lyme', 'E07000196': 'South Staffordshire', 'E07000197': 'Stafford', 'E07000198': 'Staffordshire Moorlands', 'E07000199': 'Tamworth', 'E07000200': 'Babergh', 'E07000202': 'Ipswich', 'E07000203': 'Mid Suffolk', 'E07000207': 'Elmbridge', 'E07000208': 'Epsom and Ewell', 'E07000209': 'Guildford', 'E07000210': 'Mole Valley', 'E07000211': 'Reigate and Banstead', 'E07000212': 'Runnymede', 'E07000213': 'Spelthorne', 'E07000214': 'Surrey Heath', 'E07000215': 'Tandridge', 'E07000216': 'Waverley', 'E07000217': 'Woking', 'E07000218': 'North Warwickshire', 'E07000219': 'Nuneaton and Bedworth', 'E07000220': 'Rugby', 'E07000221': 'Stratford-on-Avon', 'E07000222': 'Warwick', 'E07000223': 'Adur', 'E07000224': 'Arun', 'E07000225': 'Chichester', 'E07000226': 'Crawley', 'E07000227': 'Horsham', 'E07000228': 'Mid Sussex', 'E07000229': 'Worthing', 'E07000234': 'Bromsgrove', 'E07000235': 'Malvern Hills', 'E07000236': 'Redditch', 'E07000237': 'Worcester', 'E07000238': 'Wychavon', 'E07000239': 'Wyre Forest', 'E07000240': 'St Albans', 'E07000241': 'Welwyn Hatfield', 'E07000242': 'East Hertfordshire', 'E07000243': 'Stevenage', 'E07000244': 'East Suffolk', 'E07000245': 'West Suffolk', 'E07000246': 'Somerset West and Taunton', 'E08000001': 'Bolton', 'E08000002': 'Bury', 'E08000003': 'Manchester', 'E08000004': 'Oldham', 'E08000005': 'Rochdale', 'E08000006': 'Salford', 'E08000007': 'Stockport', 'E08000008': 'Tameside', 'E08000009': 'Trafford', 'E08000010': 'Wigan', 'E08000011': 'Knowsley', 'E08000012': 'Liverpool', 'E08000013': 'St. Helens', 'E08000014': 'Sefton', 'E08000015': 'Wirral', 'E08000016': 'Barnsley', 'E08000017': 'Doncaster', 'E08000018': 'Rotherham', 'E08000019': 'Sheffield', 'E08000021': 'Newcastle upon Tyne', 'E08000022': 'North Tyneside', 'E08000023': 'South Tyneside', 'E08000024': 'Sunderland', 'E08000025': 'Birmingham', 'E08000026': 'Coventry', 'E08000027': 'Dudley', 'E08000028': 'Sandwell', 'E08000029': 'Solihull', 'E08000030': 'Walsall', 'E08000031': 'Wolverhampton', 'E08000032': 'Bradford', 'E08000033': 'Calderdale', 'E08000034': 'Kirklees', 'E08000035': 'Leeds', 'E08000036': 'Wakefield', 'E08000037': 'Gateshead', 'E09000001': 'City of London', 'E09000002': 'Barking and Dagenham', 'E09000003': 'Barnet', 'E09000004': 'Bexley', 'E09000005': 'Brent', 'E09000006': 'Bromley', 'E09000007': 'Camden', 'E09000008': 'Croydon', 'E09000009': 'Ealing', 'E09000010': 'Enfield', 'E09000011': 'Greenwich', 'E09000012': 'Hackney and City of London', 'E09000013': 'Hammersmith and Fulham', 'E09000014': 'Haringey', 'E09000015': 'Harrow', 'E09000016': 'Havering', 'E09000017': 'Hillingdon', 'E09000018': 'Hounslow', 'E09000019': 'Islington', 'E09000020': 'Kensington and Chelsea', 'E09000021': 'Kingston upon Thames', 'E09000022': 'Lambeth', 'E09000023': 'Lewisham', 'E09000024': 'Merton', 'E09000025': 'Newham', 'E09000026': 'Redbridge', 'E09000027': 'Richmond upon Thames', 'E09000028': 'Southwark', 'E09000029': 'Sutton', 'E09000030': 'Tower Hamlets', 'E09000031': 'Waltham Forest', 'E09000032': 'Wandsworth', 'E09000033': 'Westminster', 'N09000001': 'Antrim and Newtownabbey', 'N09000002': 'Armagh City, Banbridge and Craigavon', 'N09000003': 'Belfast', 'N09000004': 'Causeway Coast and Glens', 'N09000005': 'Derry City and Strabane', 'N09000006': 'Fermanagh and Omagh', 'N09000007': 'Lisburn and Castlereagh', 'N09000008': 'Mid and East Antrim', 'N09000009': 'Mid Ulster', 'N09000010': 'Newry, Mourne and Down', 'N09000011': 'Ards and North Down', 'S08000015': 'Ayrshire and Arran', 'S08000016': 'Borders', 'S08000017': 'Dumfries and Galloway', 'S08000019': 'Forth Valley', 'S08000020': 'Grampian', 'S08000022': 'Highland', 'S08000024': 'Lothian', 'S08000025': 'Orkney', 'S08000026': 'Shetland', 'S08000028': 'Western Isles', 'S08000029': 'Fife', 'S08000030': 'Tayside', 'S08000031': 'Greater Glasgow and Clyde', 'S08000032': 'Lanarkshire', 'W06000001': 'Isle of Anglesey', 'W06000002': 'Gwynedd', 'W06000003': 'Conwy', 'W06000004': 'Denbighshire', 'W06000005': 'Flintshire', 'W06000006': 'Wrexham', 'W06000008': 'Ceredigion', 'W06000009': 'Pembrokeshire', 'W06000010': 'Carmarthenshire', 'W06000011': 'Swansea', 'W06000012': 'Neath Port Talbot', 'W06000013': 'Bridgend', 'W06000014': 'Vale of Glamorgan', 'W06000015': 'Cardiff', 'W06000016': 'Rhondda Cynon Taf', 'W06000018': 'Caerphilly', 'W06000019': 'Blaenau Gwent', 'W06000020': 'Torfaen', 'W06000021': 'Monmouthshire', 'W06000022': 'Newport', 'W06000023': 'Powys', 'W06000024': 'Merthyr Tydfil'}

scotcode= {'Ayrshire and Arran':'S08000015', 'Borders':'S08000016' , 'Dumfries and Galloway':'S08000017', 'Forth Valley':'S08000019',  'Grampian':'S08000020', 'Highland':'S08000022', 'Lothian':'S08000024', 'Orkney':'S08000025' , 'Shetland':'S08000026', 'Western Isles':'S08000028' ,'Fife':'S08000029', 'Tayside':'S08000030', 'Greater Glasgow and Clyde':'S08000031', 'Lanarkshire':'S08000032'}
	
ni_codes={'Antrim & Newtownabbey':'N09000001','Belfast':'N09000003', 'Causeway Coast & Glens':'N09000004', 'Derry City & Strabane':'N09000005', "Ards & North Down":"N09000011","Armagh City, Banbridge & Craigavon": "N09000002",'Fermanagh & Omagh':'N09000006', 'Lisburn & Castlereagh':'N09000007', 'Mid & East Antrim':'N09000008',
'Mid Ulster':'N09000009', 'Newry, Mourne & Down':'N09000010'}



nation={'E06000001': 'England', 'E06000002': 'England', 'E06000003': 'England', 'E06000004': 'England', 'E06000005': 'England', 'E06000006': 'England', 'E06000007': 'England', 'E06000008': 'England', 'E06000009': 'England', 'E06000010': 'England', 'E06000011': 'England', 'E06000012': 'England', 'E06000013': 'England', 'E06000014': 'England', 'E06000015': 'England', 'E06000016': 'England', 'E06000017': 'England', 'E06000018': 'England', 'E06000019': 'England', 'E06000020': 'England', 'E06000021': 'England', 'E06000022': 'England', 'E06000023': 'England', 'E06000024': 'England', 'E06000025': 'England', 'E06000026': 'England', 'E06000027': 'England', 'E06000030': 'England', 'E06000031': 'England', 'E06000032': 'England', 'E06000033': 'England', 'E06000034': 'England', 'E06000035': 'England', 'E06000036': 'England', 'E06000037': 'England', 'E06000038': 'England', 'E06000039': 'England', 'E06000040': 'England', 'E06000041': 'England', 'E06000042': 'England', 'E06000043': 'England', 'E06000044': 'England', 'E06000045': 'England', 'E06000046': 'England', 'E06000047': 'England', 'E06000049': 'England', 'E06000050': 'England', 'E06000051': 'England', 'E06000052': 'England', 'E06000054': 'England', 'E06000055': 'England', 'E06000056': 'England', 'E06000057': 'England', 'E06000058': 'England', 'E06000059': 'England', 'E06000060': 'England', 'E07000008': 'England', 'E07000009': 'England', 'E07000010': 'England', 'E07000011': 'England', 'E07000012': 'England', 'E07000026': 'England', 'E07000027': 'England', 'E07000028': 'England', 'E07000029': 'England', 'E07000030': 'England', 'E07000031': 'England', 'E07000032': 'England', 'E07000033': 'England', 'E07000034': 'England', 'E07000035': 'England', 'E07000036': 'England', 'E07000037': 'England', 'E07000038': 'England', 'E07000039': 'England', 'E07000040': 'England', 'E07000041': 'England', 'E07000042': 'England', 'E07000043': 'England', 'E07000044': 'England', 'E07000045': 'England', 'E07000046': 'England', 'E07000047': 'England', 'E07000061': 'England', 'E07000062': 'England', 'E07000063': 'England', 'E07000064': 'England', 'E07000065': 'England', 'E07000066': 'England', 'E07000067': 'England', 'E07000068': 'England', 'E07000069': 'England', 'E07000070': 'England', 'E07000071': 'England', 'E07000072': 'England', 'E07000073': 'England', 'E07000074': 'England', 'E07000075': 'England', 'E07000076': 'England', 'E07000077': 'England', 'E07000078': 'England', 'E07000079': 'England', 'E07000080': 'England', 'E07000081': 'England', 'E07000082': 'England', 'E07000083': 'England', 'E07000084': 'England', 'E07000085': 'England', 'E07000086': 'England', 'E07000087': 'England', 'E07000088': 'England', 'E07000089': 'England', 'E07000090': 'England', 'E07000091': 'England', 'E07000092': 'England', 'E07000093': 'England', 'E07000094': 'England', 'E07000095': 'England', 'E07000096': 'England', 'E07000098': 'England', 'E07000099': 'England', 'E07000102': 'England', 'E07000103': 'England', 'E07000105': 'England', 'E07000106': 'England', 'E07000107': 'England', 'E07000108': 'England', 'E07000109': 'England', 'E07000110': 'England', 'E07000111': 'England', 'E07000112': 'England', 'E07000113': 'England', 'E07000114': 'England', 'E07000115': 'England', 'E07000116': 'England', 'E07000117': 'England', 'E07000118': 'England', 'E07000119': 'England', 'E07000120': 'England', 'E07000121': 'England', 'E07000122': 'England', 'E07000123': 'England', 'E07000124': 'England', 'E07000125': 'England', 'E07000126': 'England', 'E07000127': 'England', 'E07000128': 'England', 'E07000129': 'England', 'E07000130': 'England', 'E07000131': 'England', 'E07000132': 'England', 'E07000133': 'England', 'E07000134': 'England', 'E07000135': 'England', 'E07000136': 'England', 'E07000137': 'England', 'E07000138': 'England', 'E07000139': 'England', 'E07000140': 'England', 'E07000141': 'England', 'E07000142': 'England', 'E07000143': 'England', 'E07000144': 'England', 'E07000145': 'England', 'E07000146': 'England', 'E07000147': 'England', 'E07000148': 'England', 'E07000149': 'England', 'E07000150': 'England', 'E07000151': 'England', 'E07000152': 'England', 'E07000153': 'England', 'E07000154': 'England', 'E07000155': 'England', 'E07000156': 'England', 'E07000163': 'England', 'E07000164': 'England', 'E07000165': 'England', 'E07000166': 'England', 'E07000167': 'England', 'E07000168': 'England', 'E07000169': 'England', 'E07000170': 'England', 'E07000171': 'England', 'E07000172': 'England', 'E07000173': 'England', 'E07000174': 'England', 'E07000175': 'England', 'E07000176': 'England', 'E07000177': 'England', 'E07000178': 'England', 'E07000179': 'England', 'E07000180': 'England', 'E07000181': 'England', 'E07000187': 'England', 'E07000188': 'England', 'E07000189': 'England', 'E07000192': 'England', 'E07000193': 'England', 'E07000194': 'England', 'E07000195': 'England', 'E07000196': 'England', 'E07000197': 'England', 'E07000198': 'England', 'E07000199': 'England', 'E07000200': 'England', 'E07000202': 'England', 'E07000203': 'England', 'E07000207': 'England', 'E07000208': 'England', 'E07000209': 'England', 'E07000210': 'England', 'E07000211': 'England', 'E07000212': 'England', 'E07000213': 'England', 'E07000214': 'England', 'E07000215': 'England', 'E07000216': 'England', 'E07000217': 'England', 'E07000218': 'England', 'E07000219': 'England', 'E07000220': 'England', 'E07000221': 'England', 'E07000222': 'England', 'E07000223': 'England', 'E07000224': 'England', 'E07000225': 'England', 'E07000226': 'England', 'E07000227': 'England', 'E07000228': 'England', 'E07000229': 'England', 'E07000234': 'England', 'E07000235': 'England', 'E07000236': 'England', 'E07000237': 'England', 'E07000238': 'England', 'E07000239': 'England', 'E07000240': 'England', 'E07000241': 'England', 'E07000242': 'England', 'E07000243': 'England', 'E07000244': 'England', 'E07000245': 'England', 'E07000246': 'England', 'E08000001': 'England', 'E08000002': 'England', 'E08000003': 'England', 'E08000004': 'England', 'E08000005': 'England', 'E08000006': 'England', 'E08000007': 'England', 'E08000008': 'England', 'E08000009': 'England', 'E08000010': 'England', 'E08000011': 'England', 'E08000012': 'England', 'E08000013': 'England', 'E08000014': 'England', 'E08000015': 'England', 'E08000016': 'England', 'E08000017': 'England', 'E08000018': 'England', 'E08000019': 'England', 'E08000021': 'England', 'E08000022': 'England', 'E08000023': 'England', 'E08000024': 'England', 'E08000025': 'England', 'E08000026': 'England', 'E08000027': 'England', 'E08000028': 'England', 'E08000029': 'England', 'E08000030': 'England', 'E08000031': 'England', 'E08000032': 'England', 'E08000033': 'England', 'E08000034': 'England', 'E08000035': 'England', 'E08000036': 'England', 'E08000037': 'England', 'E09000001': 'England', 'E09000002': 'England', 'E09000003': 'England', 'E09000004': 'England', 'E09000005': 'England', 'E09000006': 'England', 'E09000007': 'England', 'E09000008': 'England', 'E09000009': 'England', 'E09000010': 'England', 'E09000011': 'England', 'E09000012': 'England', 'E09000013': 'England', 'E09000014': 'England', 'E09000015': 'England', 'E09000016': 'England', 'E09000017': 'England', 'E09000018': 'England', 'E09000019': 'England', 'E09000020': 'England', 'E09000021': 'England', 'E09000022': 'England', 'E09000023': 'England', 'E09000024': 'England', 'E09000025': 'England', 'E09000026': 'England', 'E09000027': 'England', 'E09000028': 'England', 'E09000029': 'England', 'E09000030': 'England', 'E09000031': 'England', 'E09000032': 'England', 'E09000033': 'England', 'E06000053': 'England','N09000001': 'Northern Ireland', 'N09000002': 'Northern Ireland', 'N09000003': 'Northern Ireland', 'N09000004': 'Northern Ireland', 'N09000005': 'Northern Ireland', 'N09000006': 'Northern Ireland', 'N09000007': 'Northern Ireland', 'N09000008': 'Northern Ireland', 'N09000009': 'Northern Ireland', 'N09000010': 'Northern Ireland', 'N09000011': 'Northern Ireland', 'S08000015': 'Scotland', 'S08000016': 'Scotland', 'S08000017': 'Scotland', 'S08000019': 'Scotland', 'S08000020': 'Scotland', 'S08000022': 'Scotland', 'S08000024': 'Scotland', 'S08000025': 'Scotland', 'S08000026': 'Scotland', 'S08000028': 'Scotland', 'S08000029': 'Scotland', 'S08000030': 'Scotland', 'S08000031': 'Scotland', 'S08000032': 'Scotland', 'W06000001': 'Wales', 'W06000002': 'Wales', 'W06000003': 'Wales', 'W06000004': 'Wales', 'W06000005': 'Wales', 'W06000006': 'Wales', 'W06000008': 'Wales', 'W06000009': 'Wales', 'W06000010': 'Wales', 'W06000011': 'Wales', 'W06000012': 'Wales', 'W06000013': 'Wales', 'W06000014': 'Wales', 'W06000015': 'Wales', 'W06000016': 'Wales', 'W06000018': 'Wales', 'W06000019': 'Wales', 'W06000020': 'Wales', 'W06000021': 'Wales', 'W06000022': 'Wales', 'W06000023': 'Wales', 'W06000024': 'Wales'}

def week(number):
    day,month,year=weeks[number]
    return pytz.utc.localize(datetime(year, month, day))

 
def sunday(number):
    day,month,year=weeks[number]
    return pytz.utc.localize(datetime(year, month, day)+timedelta(2))
    

def make_index():
    _i={}
    for name,areacode in stored_names:
        _i[areacode]=name
    return _i
    