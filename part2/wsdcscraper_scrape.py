import simplejson as json
import requests
import pickle as pkl

class DanceScraper:

    API_URL = 'https://points.worldsdc.com/lookup/find'

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
        response = requests.post(self.API_URL, data=data)
        return response.json()
    
    def run(self):
        raw_data = []
        file = open('raw_data.p', 'wb')
        # 16981 is the highest WSDC number on 2/2/2018
        for wsdc_id in range(16981):
            try: 
                data = self.get_info(wsdc_id)
                if 'placements' in data:
                    raw_data.append(data)
                    pkl.dump(raw_data, file)
                    print(wsdc_id)
            except ValueError as IndexError:
                continue
        file.close()

if __name__ == '__main__':
    scraper = DanceScraper()
    scraper.run()