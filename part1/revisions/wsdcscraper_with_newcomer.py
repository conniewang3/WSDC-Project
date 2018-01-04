# Importing libraries
import simplejson as json
import requests
import pandas as pd

class DanceScraper:

    API_url = 'https://points.worldsdc.com/lookup/find'

    # This is a pandas dataframe that will contain variables of interest (e.g. 
    # points in each division, region, etc.) across the top, with one dancer 
    # per row
    scraped_info = pd.DataFrame()

    def get_info(self, number):
        '''
        Sends a post request to return the info located in a specific dancer 
        file, identified by WSDC ID number 
        '''
    
        # This is the data required by the api to send back the info
        data = {
        'q': number
        }

        # Making the post request and returning it as a dictionary
        response = requests.post(self.API_url, data=data)
        return response.json()

    def parse_response(self, response):
        '''
        Parses response (result of get_info -- a dictionary) to fill in one 
        entry of scraped_info
        '''

        new_entry = {
        'id': response['dancer']['wscid'], # WSDC ID number
        'division': 'Newcomer',   # Current competition division
        'role': '',       # Primary role (follower/leader)
        'region': '',     # Estimated region of residence
        'new_points': 0,  # Number of points in Newcomer
        'nov_points': 0,  # Number of points in Novice
        'int_points': 0,  # Number of points in Intermediate
        'adv_points': 0,  # Number of points in Advanced
        'als_points': 0,  # Number of points in All-Star
        'end_date': '',   # Date of most recent point entered in nov-als
        'new_start': '',  # Date of first Newcomer point
        'new_end': '',    # Date of last Newcomer point
        'nov_start': '',  # Date of first Novice point
        'nov_end': '',    # Date of last Novice point
        'int_start': '',  # Date of first Intermediate point
        'int_end': '',    # Date of last Intermediate point
        'adv_start': '',  # Date of first Advanced point
        'adv_end': '',    # Date of last Advanced point
        'als_start': '',  # Date of first All-Star point
        'als_end': '',    # Date of last All-Star point
        'new_count': 0,   # Number of events with Newcomer points recorded
        'nov_count': 0,   # Number of events with Novice points recorded
        'int_count': 0,   # Number of events with Intermediate points recorded
        'adv_count': 0,   # Number of events with Advanced points recorded
        'als_count': 0,   # Number of events with All-Star points recorded
        'nov_place': 0,   # 1-5 tier 3 and 1-3 tier 2 placements in Novice
        'int_place': 0,   # 1-5 tier 3 and 1-3 tier 2 placements in Intermediate
        'adv_place': 0,   # 1-5 tier 3 and 1-3 tier 2 placements in Advanced
        'als_place': 0,   # 1-5 tier 3 and 1-3 tier 2 placements in All-Star
        'nov_first': False,  # Indicates whether placed first in Novice
        'int_first': False,  # Indicates whether placed first in Intermediate
        'adv_first': False,  # Indicates whether placed first in Advanced
        'als_first': False,  # Indicates whether placed first in All-Star
        'adv_3y': 0, # Number of Advanced points in the last 3 years
        'als_3y': 0, # Number of All-Star points in the last 3 years
        }
        
        # Some early entries to the WSDC database have no placements at all;
        # Some entries have only non-West-Coast-Swing placements
        # Let's ignore these.
        if response['placements'] == []:
            return new_entry
        if 'West Coast Swing' not in response['placements'].keys():
            return new_entry

        # This gets all placements as a list
        placements = response['placements']['West Coast Swing'] 

        # Primary role determined by role in first entry
        new_entry['role'] = placements[0]['competitions'][0]['role']

        # Each item in the list is a dictionary representing a division; iterate 
        # through divisions, saving data from the ones we're interested in
        for entry in placements:

            # This gets name of the division we're looking at
            division = entry['division']['name'] 
            
            # This gets a list of recorded comps from the division
            comps = entry['competitions']
            
            # This collects the points granted for every comp in the list
            points = [event['points'] for event in comps]
            
            # This collects the placements for every comp in the list
            results = [event['result'] for event in comps]
            
            # This collects the locations of every comp in the list
            locations = [event['event']['location'] for event in comps]

            # This indicates if each comp in the list is within the last 3 years
            dates = [event['event']['date'] for event in comps]
            is_relevant = [int(date.split()[1]) > 2015 for date in dates]
            
            # This stores information by division
            if division == 'Newcomer':
                new_entry['new_points'] = entry['total_points']
                new_entry['new_end'] = comps[0]['event']['date']
                new_entry['new_start'] = comps[-1]['event']['date']
                new_entry['new_count'] = len(comps)
                continue
            if division == 'Novice':
                new_entry['nov_points'] = entry['total_points']
                new_entry['nov_end'] = comps[0]['event']['date']
                new_entry['nov_start'] = comps[-1]['event']['date']
                new_entry['nov_count'] = len(comps)
                new_entry['nov_place'] = sum(i > 5 for i in points)
                new_entry['nov_first'] = '1' in results
                continue
            if division == 'Intermediate':
                new_entry['int_points'] = entry['total_points']
                new_entry['int_end'] = comps[0]['event']['date']
                new_entry['int_start'] = comps[-1]['event']['date']
                new_entry['int_count'] = len(comps)
                new_entry['int_place'] = sum(i > 5 for i in points)
                new_entry['int_first'] = '1' in results
                continue
            if division == 'Advanced':
                new_entry['adv_points'] = entry['total_points']
                new_entry['adv_end'] = comps[0]['event']['date']
                new_entry['adv_start'] = comps[-1]['event']['date']
                new_entry['adv_count'] = len(comps)
                new_entry['adv_place'] = sum(i > 5 for i in points)
                new_entry['adv_first'] = '1' in results
                new_entry['adv_3y'] = sum(a*b for a,b in zip(points, 
                                                             is_relevant))
                continue
            if division == 'All-Stars':
                new_entry['als_points'] = entry['total_points']
                new_entry['als_end'] = comps[0]['event']['date']
                new_entry['als_start'] = comps[-1]['event']['date']
                new_entry['als_count'] = len(comps)
                new_entry['als_place'] = sum(i > 5 for i in points)
                new_entry['als_first'] = '1' in results
                new_entry['als_3y'] = sum(a*b for a,b in zip(points, 
                                                             is_relevant))
                continue
            else: 
                continue

        # This gets the date of the most recently entered competition, mostly 
        # (ignores when events are recorded out of chronological order and when
        # the most recent event for an All-Star is combined adv/als and recorded 
        # as adv, because I decided those didn't have a large enough impact to 
        # be worth the effort)
        end_dates = [new_entry['new_end'], new_entry['nov_end'], new_entry['int_end'], 
                    new_entry['adv_end'], new_entry['als_end']]
        for date in end_dates:
            if date != '':
                new_entry['end_date'] = date 

        # This determines what division this person is currently competing in
        if new_entry['nov_points'] != 0:
            new_entry['division'] = 'Novice'
        if new_entry['nov_points'] >= 15:
            new_entry['division'] = 'Intermediate'
        if new_entry['int_points'] >= 30:
            new_entry['division'] = 'Advanced'
        # Since All-Star/Champ is opt-in, consider a competitor an 
        # All-Star/Champ only if they have non-zero All-Star points within 
        # the last 3 years
        if (new_entry['als_points'] > 0 and
            int(new_entry['als_end'].split()[1]) > 2014):
            new_entry['division'] = 'All-Star'

        # This estimates what region the competitor lives in.
        # Region definitions:
        # West Coast: West Coast US plus British Columbia
        # Midwest+TX: Midwest US
        # East Coast: East Coast US plus the rest of Canada
        # Other: Singapore, South Korea, Australia, New Zealand, Brazil
        # Europe: All else
        # Region is defined as the one with the most recorded events, or for 
        # Europe and Other, at least [5 for Europe, 3 for Other] events in the 
        # region OR at least 1 such event and less than 10 events total
        west_coast = [', WA', ', OR', ', CA', ' NV', ' AZ', 'Vancouver, Canada', 
                      ', BC', 'Oregon']
        midwest = [', CO', ', MO', ', OK', ', TX', ', LA', ', IL', ', WI', 
                   ', KY', ', MI', 'Texas', ', OH', ', IN', ', MN']
        east_coast = [', QC', ', NY', ', MA', ', PA', ', NJ', ', NC', ', GA', 
                      ', FL', ', MD', ', DC', ', NY', 'Alberta', 'Canada', 
                      ', VA', ', TN', 'Philadelphia', ', SC', ', CT']
        other = ['Singapore', 'Korea', 'Australia', 'New Zealand', 'Brazil']
        counts = {'West Coast': 0, 'Midwest': 0, 'East Coast': 0, 
                  'Other': 0, 'Europe': 0}
        for location in locations:
            if any(x in location for x in west_coast):
                counts['West Coast'] += 1
                continue
            if any(x in location for x in midwest):
                counts['Midwest'] += 1
                continue
            if any(x in location for x in east_coast):
                counts['East Coast'] += 1
                continue
            if any(x in location for x in other):
                counts['Other'] += 1
                continue
            else: 
                counts['Europe'] += 1

        new_entry['region'] = max(counts, key=counts.get)
        if counts['Europe'] >= 5 or (counts['Europe'] >= 1 and 
                                     sum(counts.values()) < 10):
            new_entry['region'] = 'Europe'
        if counts['Other'] >= 3 or (counts['Other'] >= 1 and 
                                     sum(counts.values()) < 10):
            new_entry['region'] = 'Other'

        return new_entry
    
    def run(self):
        for wsdc_id in range(16802):
            try:
                data = self.get_info(wsdc_id)
                # only cases with valid WSDC IDs
                if len(data) > 2:
                    parsed = self.parse_response(data)
                    # Only accept competitors with at least 1 novice comp
                    if (
                        parsed['nov_count'] > 0 or
                        parsed['new_count'] > 0
                        ):
                        self.scraped_info = self.scraped_info.append(parsed, 
                                            ignore_index=True)
                        print(wsdc_id)
            except ValueError as IndexError:
                continue
        self.scraped_info.to_csv('data.csv')

if __name__ == '__main__':
    scraper = DanceScraper()
    scraper.run()