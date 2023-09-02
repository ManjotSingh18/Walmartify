from api import WEBAPI
import geocoder
import json
import requests
import re
import xlsxwriter
from collections import defaultdict
import string
import os
import shutil
import uuid
import time
import base64

#Locator API
ALPHA=list(string.ascii_uppercase)
class LocatorApi(WEBAPI):
    def __init__(self, lat: int, long:int, storequery: str, defaulto='walmart'):
        self.lat=lat
        self.long=long
        self.storequery=defaulto
        self.apikey='WfOlNPnPHQeTBmbGulDFQoxZljpMpmYS' #TomTom APIKEY
        #User based data collection on grocery stores inserted into a data file
        self.stores=[]
    #Load Nearby Grocery Locations
    def load_data(self):
        url = f'https://api.tomtom.com/search/2/poiSearch/{self.storequery}.json?lat={self.lat}&lon={self.long}&categorySet=7327%2C9361023%2C9361022%2C9361021%2C9361066%2C9361%2C7332005&view=Unified&relatedPois=off&key={self.apikey}'
        data=super()._download_url(url)
        dupremove=set()
        for stores in data['results']:
            try:
                if stores['address']['freeformAddress'] in dupremove:
                    pass
                else:
                    dupremove.add(stores['address']['freeformAddress'])
                    self.stores.append((stores['poi']['name'],(stores['poi']['url'], stores['address']['freeformAddress'])))
            except:
                pass
#Main Application
class MainApplication:
    def __init__(self):
        print("Welcome to the Walmart-Spreadsheet-Generator\n -Please ensure location services are on to record data on stores in proximity.\n -Also, allow access to the file system specifically the current user's document folder as a folder will be created to store the generated sheets")
        storequery='Walmart'
        #try:
        searchquery=str(input('\nSearch and Record Product (ex. Milk) ("Q" to quit) ("R" to remove ProductSheets Folder) ("D filename" to delete specific sheet): '))
        newpath = r'C:/Users/{}/Documents/ProductSheets'.format(os.getlogin())
        
        while searchquery != 'Q':
            #try:
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                if searchquery == 'Q':
                    print('Exited')
                    quit()
                elif searchquery == 'R':
                    shutil.rmtree('C:/Users/{}/Documents/ProductSheets/'.format(os.getlogin()))
                    print('ProductSheets folder and contents removed')
                    searchquery=str(input('\nSearch and Record Product (ex. Milk) ("Q" to quit) ("R" to remove ProductSheets Folder) ("D filename" to delete specific sheet): '))
                elif searchquery.strip().split()[0] == 'D':
                    #try:
                        file=searchquery.strip().split(' ',1)[1]
                        os.remove('C:/Users/{}/Documents/ProductSheets/{}.xlsx'.format(os.getlogin(), file.lower()))
                        print('{} spreadsheet has been deleted from ProductSheets folder'.format(file))
                        searchquery=str(input('\nSearch and Record Product (ex. Milk) ("Q" to quit) ("R" to remove ProductSheets Folder) ("D filename" to delete specific sheet): '))
                    #except:
                        #print('File not found')
                        #searchquery=str(input('\nSearch and Record Product (ex. Milk) ("Q" to quit) ("R" to remove ProductSheets Folder) ("D filename" to delete specific sheet): '))
                #CurrentLocation [Lat, Long] prodcut of gecoder.ip method
                else:
                    print('Loading...')
                    cl = geocoder.ip('me')
                    locator=LocatorApi(cl.lat,cl.lng,storequery)
                    locator.load_data()
                    store={}
                    store[locator.storequery.lower()] = locator.stores
                    W=WalmartScraper()
                    itemdict=W.Process(searchquery, walmartstores=store[locator.storequery.lower()])
                    workbook = xlsxwriter.Workbook('C:/Users/{}/Documents/ProductSheets/{}.xlsx'.format(os.getlogin(), searchquery.lower()))
                    worksheet = workbook.add_worksheet()
                    data=[]
                    for product, prices in itemdict.items():
                        data.append([product]+prices)
                    locations=[{'header': 'Product'}]+[{'header': walmart[1][1]} for walmart in store[locator.storequery.lower()]]
        
                    worksheet.add_table('B1:{}{}'.format(ALPHA[len(store[locator.storequery.lower()])], len(data)), {'data': data, 'columns': locations})
                    workbook.close()
                    print('Done, sheet has been recorded in documents directory within the ProductSheets folder')
                    searchquery=str(input('\nSearch and Record Product (ex. Milk) ("Q" to quit) ("R" to remove ProductSheets Folder) ("D filename" to delete specific sheet): '))
                #except:
                    #print('Invalid Input')   
                    #searchquery=str(input('\nSearch and Record Product (ex. Milk) ("Q" to quit) ("R" to remove ProductSheets Folder) ("D filename" to delete specific sheet): ')) 
        #except:
            #print('Invalid Input')
            #MainApplication()
    #StoreSorter
        
        
        
#Walmart Scraper
class WalmartScraper:
    def Process(self, searchquery, walmartstores=None):
        itemdict=defaultdict(list)
        ouruid=uuid.uuid4()
        currenttime=int(time.time())
        for walmart in walmartstores:
            currenturl=walmart[1][0]
            id_=re.compile(r'\d\d\d\d')
            currentlocation=walmart[1][1]
            cityf=currentlocation.split(',')
            try:
                currentstoreid=id_.search(currenturl).group()
                currentzipcode=walmart[1][1].split(' ')[-1]
                currentstatecode=walmart[1][1].split(' ')[-2]

            except:
                pass
            locdata= {
            "intent":"SHIPPING",
            "isExplicit":False,
            "storeIntent":"PICKUP",
            "mergeFlag":False,
            "isDefaulted":False,
            "pickup":{
                "nodeId":str(currentstoreid),
                "timestamp":currenttime,
                "selectionType":"LS_SELECTED"
            },
            "shippingAddress":{
                "timestamp":currenttime,
                "type":"partial-location",
                "giftAddress":False,
                "postalCode":str(currentzipcode),
                "city": str(cityf[1].strip(' ')),
                "state":str(currentstatecode),
                "deliveryStoreList":[
                    {
                        "nodeId":str(currentstoreid),
                        "type":"DELIVERY",
                        "timestamp":currenttime,
                        "selectionType":"LS_SELECTED",
                        "selectionSource":"TETHERED"
                    }
                ]
            },
            "postalCode":{
                "timestamp":currenttime,
                "base":str(currentzipcode)
            },
            "mp":[
                
            ],
            "validateKey":f"prod:v2:{str(ouruid)}"
            }
            stringify=json.dumps(locdata)
            locplaceholder=base64.b64encode(stringify.encode('utf-8'))
            decodeholder=str(locplaceholder.decode())
            url = f"https://www.walmart.com/orchestra/snb/graphql/Search/540c634cf76b265232e508bd5eca435cb7aeaf9620cba568d3d0c1fc5233cc7f/search?variables=%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22{searchquery}%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22{searchquery}%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22fitmentFieldParams%22%3A%7B%22powerSportEnabled%22%3Atrue%2C%22dynamicFitmentEnabled%22%3Atrue%2C%22extendedAttributesEnabled%22%3Afalse%7D%2C%22fitmentSearchParams%22%3A%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22{searchquery}%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22{searchquery}%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22cat_id%22%3A%22%22%2C%22_be_shelf_id%22%3A%22%22%7D%2C%22enableFashionTopNav%22%3Afalse%2C%22enableRelatedSearches%22%3Atrue%2C%22enablePortableFacets%22%3Atrue%2C%22enableFacetCount%22%3Atrue%2C%22fetchMarquee%22%3Atrue%2C%22fetchSkyline%22%3Atrue%2C%22fetchGallery%22%3Afalse%2C%22fetchSbaTop%22%3Atrue%2C%22fetchDac%22%3Afalse%2C%22tenant%22%3A%22WM_GLASS%22%2C%22enableFlattenedFitment%22%3Afalse%2C%22enableMultiSave%22%3Afalse%2C%22pageType%22%3A%22SearchPage%22%7D"

            payload = {}
            headers = {
            'authority': 'www.walmart.com',
            'accept': 'application/json',
            'accept-language': 'en-US',
            'content-type': 'application/json',
            'cookie': f'ak_bmsc=67E41BB3A759BD8B4FC661E10C8D2C95~000000000000000000000000000000~YAAQVf4ZuFRzJEyKAQAAdKnhUhSQqPteSZ1toZEfcCBKPn9dyEZCH/ikuYbhY8zoTUlYcE1id3nnGs0XEKFWPTdnFond1KyyjijGEZLhrZzeY7RPPMDGoJkfefDbndDPGS1Sb45OAeUVKwiEWiCPZwkNzA0wezTWu6+6eJyTar4xg5otZWn5j6AdMw2/16ni+hqApLbfxU80QLd0ukTlj1/+UgenBQJThOuEFNpp992YlyLHE6FioTJTvqqvVdHKVqple5iI9iVFoQ+XTNLTiIhXr202ZDtkDkCrIffGVcFQVEB/wmwVHBgFH/N2BA10zz1zikO0KadoUxCypKjylRJUmYa5++96Cm0AWAtdVqeybnW21uEXg0EJO9CR5xVGG7J6veT+GGRW; vtc=VXl_LH4Xz63nofFYljvPA8; bstc=VXl_LH4Xz63nofFYljvPA8; adblocked=false; pxcts=a2aba194-4917-11ee-a642-56676b576c71; _pxvid=a2ab950a-4917-11ee-a642-64bb8abc4e10; TBV=7; auth=MTAyOTYyMDE4fx4zuD1T9ZzEwuVH3%2FOGRHKyrVWFJGScQm6v1p555ilw8RjSkgGDti6jD%2BiXeMZMFUIbod%2BJOEIa8dv9NE%2BeW%2FJUXk%2FFPn2mVP%2F0yUZt0YbLX0to6LHJ1%2FmPrWfXATzL767wuZloTfhm7Wk2Kcjygv699%2F6tFVwuL3qJB39WKV9DQtd7UojlkbasxZMOQ3q9EccyFUBP2O4iz2%2FGUTaUUBx4MMqXoyBxgDBI4axv988UMk70P8glgOEpLOprhDfMDCcb9mgycy9jtT1uIyOBHQR6WUE9sXMbGPzYnLwv6E%2BSxx2e30M1bOaMriomyVCtOnzhPe0gHbwCGWDuWW43pVK3uxERGRSAeChUHr4cFc%2Bm9KxyZugP5TGwIxWJ%2FKlC24REbwJ3GozzfsegpNgc9ZE5WBBdZBCyKnCQAR7o6eg%3D; ACID={ouruid}; hasACID=true; locDataV3={decodeholder}; assortmentStoreId={currentstoreid}; hasLocData=1; locGuestData={decodeholder}; abqme=false; akavpau_p2=1693608676~id=1bc401eb1a07dab028aecc0b65030928',
            'device_profile_ref_id': '9HZV8KTIV06YEY3-zM7ipTMaK6F_9RI_VrCQ',
            'referer': f'https://www.walmart.com/search?q={searchquery}',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'traceparent': '00-78532d0ab66e986978f5314349ebc5ad-d560e5408c367894-00',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'wm_mp': 'true',
            'wm_page_url': f'https://www.walmart.com/search?q={searchquery}',
            'wm_qos.correlation_id': 'T1gY3mGXX8ghB6Cboziph8QX0e01gGeiMIFq',
            'x-apollo-operation-name': 'Search',
            'x-enable-server-timing': '1',
            'x-latency-trace': '1',
            'x-o-bu': 'WALMART-US',
            'x-o-ccm': 'server',
            'x-o-correlation-id': 'T1gY3mGXX8ghB6Cboziph8QX0e01gGeiMIFq',
            'x-o-gql-query': 'query Search',
            'x-o-mart': 'B2C',
            'x-o-platform': 'rweb',
            'x-o-platform-version': 'us-web-1.97.0-caf6b55-0829T1635',
            'x-o-segment': 'oaoh'
            }

            r = requests.request("GET", url, headers=headers, data=payload)
            data=json.loads(r.text)
            for items in data['data']['search']['searchResult']['itemStacks'][0]['itemsV2']:
                try:
                    itemdict[items['name']].append(float(items['priceInfo']['currentPrice']['price']))
                except KeyError:
                    pass
        return itemdict
if __name__=='__main__':
    MainApplication()
