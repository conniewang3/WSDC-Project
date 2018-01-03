# Importing libraries
import pandas as pd
import requests
import simplejson as json

API_url = 'https://points.worldsdc.com/lookup/find'
counts = pd.DataFrame()

# Starting from 8220 to approximately limit to comps after 2014
for wsdc_id in range(8220,16802):
            try:
                response = requests.post(API_url, {'q': wsdc_id}).json()
                # only cases with valid WSDC IDs containing WCS placements
                if (len(response) > 2 and
                    response['placements'] != [] and
                    'West Coast Swing' in response['placements'].keys()):
                    
                    # build list of locations of each event
                    for entry in response['placements']['West Coast Swing']:
                        locations = [comp['event']['location'] for comp in entry['competitions']]
                    
                    # assign regions for each location and count
                    west_coast = [', WA', ', OR', ', CA', ' NV', ' AZ', 'Vancouver, Canada', 
                                  ', BC', 'Oregon']
                    midwest = [', CO', ', MO', ', OK', ', TX', ', LA', ', IL', ', WI', 
                               ', KY', ', MI', 'Texas', ', OH', ', IN', ', MN']
                    east_coast = [', QC', ', NY', ', MA', ', PA', ', NJ', ', NC', ', GA', 
                                  ', FL', ', MD', ', DC', ', NY', 'Alberta', 'Canada', 
                                  ', VA', ', TN', 'Philadelphia', ', SC', ', CT']
                    other = ['Singapore', 'Korea', 'Australia', 'New Zealand', 'Brazil']
                    entry = {'West Coast': 0, 'Midwest': 0, 'East Coast': 0, 
                              'Other': 0, 'Europe': 0}
                    for location in locations:
                        if any(x in location for x in west_coast):
                            entry['West Coast'] += 1
                            continue
                        if any(x in location for x in midwest):
                            entry['Midwest'] += 1
                            continue
                        if any(x in location for x in east_coast):
                            entry['East Coast'] += 1
                            continue
                        if any(x in location for x in other):
                            entry['Other'] += 1
                            continue
                        else: 
                            entry['Europe'] += 1
                
                # append entry to counts dataframe
                counts = counts.append(entry, ignore_index=True)
                print(wsdc_id)

            except ValueError as IndexError:
                continue

# Getting sum by region
print(counts.sum())
