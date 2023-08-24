from API_Template import WEBAPI
import geocoder
import json
import requests
import re
import xlsxwriter
from collections import defaultdict
import string
import os
import shutil

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
        for walmart in walmartstores:
            currenturl=walmart[1][0]
            id_=re.compile(r'\d\d\d\d')
            currentlocation=walmart[1][1]
            try:
                currentstoreid=id_.search(currenturl).group()
                currentzipcode=walmart[1][1].split(' ')[-1]
                currentstatecode=walmart[1][1].split(' ')[-2]
            except:
                pass

            url = f"https://www.walmart.com/orchestra/snb/graphql/Search/48093560def448db9dad9bcfc8e5b556413f9bd4252bc7a300e26df3a24596b3/search?variables=%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22{searchquery}%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22pickup%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22{searchquery}%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22fitmentFieldParams%22%3A%7B%22powerSportEnabled%22%3Atrue%2C%22dynamicFitmentEnabled%22%3Atrue%2C%22extendedAttributesEnabled%22%3Afalse%7D%2C%22fitmentSearchParams%22%3A%7B%22id%22%3A%22%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22{searchquery}%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22{searchquery}%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22cat_id%22%3A%22%22%2C%22_be_shelf_id%22%3A%22%22%7D%2C%22enableFashionTopNav%22%3Afalse%2C%22enableRelatedSearches%22%3Atrue%2C%22enablePortableFacets%22%3Atrue%2C%22enableFacetCount%22%3Atrue%2C%22fetchMarquee%22%3Atrue%2C%22fetchSkyline%22%3Atrue%2C%22fetchGallery%22%3Afalse%2C%22fetchSbaTop%22%3Atrue%2C%22fetchDac%22%3Afalse%2C%22tenant%22%3A%22WM_GLASS%22%2C%22enableFlattenedFitment%22%3Afalse%2C%22enableMultiSave%22%3Afalse%2C%22pageType%22%3A%22SearchPage%22%7D"

            payload = {}
            headers = {
            'authority': 'www.walmart.com',
            'accept': 'application/json',
            'accept-language': 'en-US',
            'content-type': 'application/json',
            'cookie': f'vtc=brnh2zjPPKKKGrjlvK-guE; _pxvid=b1563a73-1cf9-11ee-abe6-3876a0424158; abqme=false; _pxhd=d9abb0f363dc7f08bc25d03a5d8ea2bba20364cadd13a978ce5768b2dd56cd5c:b184f462-1cf9-11ee-a936-488da41f4b5e; CID=b56f4f2c-4c29-448b-bd91-dd6551ab843c; hasCID=1; SPID=6a46803893dab7859a96a6ee2f9de244eb6fa2940613a63441edc2b7169a539eb3caba7e08d5691513e2ad39a772ca58myacc; type=REGISTERED; _vc=VbVpv%2FYOXHV4y8L9HK5zjP9iFr3PnPzYVFhzwunnO28%3D; sod=1688756743682-e1987cd6-3a9f-41eb-8f02-9ec1895c07df; customer=%7B%22firstName%22%3A%22Gurcharanjit%22%2C%22lastNameInitial%22%3A%22S%22%7D; _m=9; __pxvid=83fd2793-1d05-11ee-8236-0242ac120002; userContext=eyJhZGRyZXNzRGF0YSI6eyJoYXNEZWxpdmVyYWJsZUFkZHJlc3MiOnRydWV9LCJoYXNJdGVtU3Vic2NyaXB0aW9uIjpmYWxzZSwiaGFzTWVtYmVyc2hpcEluZm8iOmZhbHNlLCJpc0RlZmF1bHQiOmZhbHNlLCJwYXltZW50RGF0YSI6eyJjYXBpdGFsT25lQmFubmVyU25vb3plVFMiOjAsImhhc0NhcE9uZSI6ZmFsc2UsImhhc0NhcE9uZUxpbmtlZCI6ZmFsc2UsImhhc0NyZWRpdENhcmQiOmZhbHNlLCJoYXNEaXJlY3RlZFNwZW5kQ2FyZCI6ZmFsc2UsImhhc0VCVCI6ZmFsc2UsImhhc0dpZnRDYXJkIjpmYWxzZSwic2hvd0NhcE9uZUJhbm5lciI6dHJ1ZSwid3BsdXNOb0JlbmVmaXRCYW5uZXIiOnRydWUsInBheW1lbnRNZXRob2RUYWdzIjpbXX0sInByb2ZpbGVEYXRhIjp7ImlzQXNzb2NpYXRlIjp0cnVlLCJpc1Rlc3RBY2NvdW50IjpmYWxzZSwibWVtYmVyc2hpcE9wdEluIjp7ImlzT3B0ZWRJbiI6ZmFsc2V9LCJjdXN0b21lclR5cGUiOiJJTkRJVklEVUFMIn0sInNob3dTaWduVXBTcGxhc2giOnRydWUsInNvZE9wdGVkT3V0Ijp0cnVlLCJpYXBBc3N1cmVkIjpmYWxzZX0%3D; adblocked=false; TBV=7; userAppVersion=main-1.95.0-9f8acf-0819T1541; locDataV3=eyJpc0RlZmF1bHRlZCI6ZmFsc2UsImlzRXhwbGljaXQiOmZhbHNlLCJpbnRlbnQiOiJQSUNLVVAiLCJwaWNrdXAiOlt7ImJ1SWQiOiIwIiwibm9kZUlkIjoiNTE5MiIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsIm5vZGVUeXBlIjoiU1RPUkUiLCJhZGRyZXNzIjp7InBvc3RhbENvZGUiOiI5NTg0MiIsImFkZHJlc3NMaW5lMSI6IjU4MjEgQW50ZWxvcGUgUmQiLCJjaXR5IjoiU2FjcmFtZW50byIsInN0YXRlIjoiQ0EiLCJjb3VudHJ5IjoiVVMiLCJwb3N0YWxDb2RlOSI6Ijk1ODQyLTM5MDIifSwiZ2VvUG9pbnQiOnsibGF0aXR1ZGUiOjM4LjcwNDMxOCwibG9uZ2l0dWRlIjotMTIxLjMzMTg2MX0sImlzR2xhc3NFbmFibGVkIjp0cnVlLCJzY2hlZHVsZWRFbmFibGVkIjp0cnVlLCJ1blNjaGVkdWxlZEVuYWJsZWQiOnRydWUsImh1Yk5vZGVJZCI6IjUxOTIiLCJzdG9yZUhycyI6IjA2OjAwLTIzOjAwIiwic3VwcG9ydGVkQWNjZXNzVHlwZXMiOlsiUElDS1VQX0lOU1RPUkUiLCJBQ0MiLCJQSUNLVVBfQ1VSQlNJREUiXSwic2VsZWN0aW9uVHlwZSI6IkNVU1RPTUVSX1NFTEVDVEVEIn1dLCJzaGlwcGluZ0FkZHJlc3MiOnsiaWQiOiIxOTYxMzdkYy0xYmE3LTQ4MGQtOWE0YS00ZTJlODcwNWY2MjYiLCJhZGRyZXNzTGluZU9uZSI6Ijc3MjggUmF2ZW5zd29ydGggV2F5IiwibGF0aXR1ZGUiOjM4LjcwNDc2LCJsb25naXR1ZGUiOi0xMjEuMzM1NzQzLCJwb3N0YWxDb2RlIjoiOTU4NDMzODUwIiwiY2l0eSI6IkFudGVsb3BlIiwic3RhdGUiOiJDQSIsImNvdW50cnlDb2RlIjoiVVNBIiwiaXNBcG9GcG8iOmZhbHNlLCJpc1BvQm94IjpmYWxzZSwiYWRkcmVzc1R5cGUiOiJSRVNJREVOVElBTCIsImxvY2F0aW9uQWNjdXJhY3kiOiJoaWdoIiwibW9kaWZpZWREYXRlIjoxNTc1MDkyMzI2MDQ2LCJnaWZ0QWRkcmVzcyI6ZmFsc2UsImZpcnN0TmFtZSI6Ikd1cmNoYXJhbmppdCIsImxhc3ROYW1lIjoiU2luZ2giLCJ0aW1lWm9uZSI6IkFtZXJpY2EvTG9zX0FuZ2VsZXMifSwiYXNzb3J0bWVudCI6eyJub2RlSWQiOiI1MTkyIiwiZGlzcGxheU5hbWUiOiJTYWNyYW1lbnRvIFN1cGVyY2VudGVyIiwiaW50ZW50IjoiUElDS1VQIn0sImluc3RvcmUiOmZhbHNlLCJkZWxpdmVyeSI6eyJidUlkIjoiMCIsIm5vZGVJZCI6IjUxOTIiLCJkaXNwbGF5TmFtZSI6IlNhY3JhbWVudG8gU3VwZXJjZW50ZXIiLCJub2RlVHlwZSI6IlNUT1JFIiwiYWRkcmVzcyI6eyJwb3N0YWxDb2RlIjoiOTU4NDIiLCJhZGRyZXNzTGluZTEiOiI1ODIxIEFudGVsb3BlIFJkIiwiY2l0eSI6IlNhY3JhbWVudG8iLCJzdGF0ZSI6IkNBIiwiY291bnRyeSI6IlVTIiwicG9zdGFsQ29kZTkiOiI5NTg0Mi0zOTAyIn0sImdlb1BvaW50Ijp7ImxhdGl0dWRlIjozOC43MDQzMTgsImxvbmdpdHVkZSI6LTEyMS4zMzE4NjF9LCJpc0dsYXNzRW5hYmxlZCI6dHJ1ZSwic2NoZWR1bGVkRW5hYmxlZCI6dHJ1ZSwidW5TY2hlZHVsZWRFbmFibGVkIjp0cnVlLCJhY2Nlc3NQb2ludHMiOlt7ImFjY2Vzc1R5cGUiOiJERUxJVkVSWV9BRERSRVNTIn1dLCJodWJOb2RlSWQiOiI1MTkyIiwiaXNFeHByZXNzRGVsaXZlcnlPbmx5IjpmYWxzZSwic3VwcG9ydGVkQWNjZXNzVHlwZXMiOlsiREVMSVZFUllfQUREUkVTUyIsIkFDQyJdLCJzZWxlY3Rpb25UeXBlIjoiTFNfU0VMRUNURUQifSwicmVmcmVzaEF0IjoxNjkyNzQ4MTM2OTg2LCJ2YWxpZGF0ZUtleSI6InByb2Q6djI6YjU2ZjRmMmMtNGMyOS00NDhiLWJkOTEtZGQ2NTUxYWI4NDNjIn0%3D; assortmentStoreId={currentstoreid}; hasLocData=0; bstc=ZUqiQB2BO54mt61fQv0-qA; mobileweb=0; xpth=x-o-mart%2BB2C~x-o-mverified%2Bfalse; xpa=-5XLL|1ecvP|200gl|2c-Ep|5vEu-|8Xuun|8nAQE|Aj49u|BukPC|C2mbG|CfYKc|Cykgk|Erqn5|G-Rah|I02NK|IXu7U|Jc18f|KkThS|KvYZX|MhYKp|N6Yhp|NZCJq|PgE9q|R2vTN|R5ktD|SETkS|Svv7-|TIE1G|VCOYl|VxdQI|X78hm|YdknO|YnYws|ZMf5y|Zmyul|_4HRC|b8OpP|dDqiD|dPmpl|dayNl|h9ALg|kQp84|kylfG|m2Cb1|mC9MV|mG0oX|oZEGf|r_-Ov|t_VGX|xFt_7; exp-ck=1ecvP1BukPC1CfYKc1Erqn51IXu7U1KkThS1KvYZX1MhYKp1N6Yhp2NZCJq1PgE9q5R2vTN1R5ktD2SETkS1TIE1G1VxdQI1YnYws4Zmyul1dDqiD1dPmpl2h9ALg3kQp842kylfG1m2Cb11mC9MV2mG0oX2r_-Ov1t_VGX1; _astc=9a2b4f5e3ac98870a850f9ee17062d5b; pxcts=14fb1e64-413e-11ee-b0ce-67674476626e; xptc=assortmentStoreId%2B{currentstoreid}; wmlh=d50b10de31586e75c666a473526c7854c9ba4adcc0da05dd5828a5c9c5ab913b; xpm=1%2B1692744540%2Bbrnh2zjPPKKKGrjlvK-guE~b56f4f2c-4c29-448b-bd91-dd6551ab843c%2B0; xpqfw=1; bm_mi=650969F8292AA9B27F5A861AB25D78FC~YAAQe+kyF3T5yxqKAQAAykB3HxSyQ9La+YhGSoqnLMAPiROZgNsqyRgcbUeTTXa+jJjtdok53S9dq91/t+gtNOw6jvSWkk6r3DtehmqmjZzVWzwW3bR/GOjBehEaaBDYsVGgruPQyfvIr7z2ixobad9KBnP7Br4AG2ZHinuNy+b+bGbyKs41U8rtLmbiT3z6gRBDW7CjBd2Bn5oCvtFAkL3rmP/Hwrqtq2zoo+3UnOaL6hJx68FUA7zJjEWL8K2/cvPFnfIFeBecAnue58pXDaI2sgUK7m0MQAnVvhuRbZ2RqlCin2QE7WwK/cl5jWhKYmQ=~1; akavpau_p1=1692745625~id=9bdf2dd90a39e64c2f19a770b1332279; bm_sv=9948EB0BA2A62705F3639DD34E96C87B~YAAQe+kyFyn8yxqKAQAAQXt3HxTT1f0473+jYIOoBdt/4f1o2xf8c68fQ6LXRA27VhDGEYu5YRdBGRQfjyVG7BRpItAt/bWgeWf3kmJa4RDfECAr+HZRNsflHD5P1Gjwy+o5jOzY7MKl9pDkoJ1bjc4twtIvqfaK75SWYN3F4wAX49Y6e8KFbRwQWA2QyYJg68RcYv5V22UMweK/D19QEZjjoOSVSIVu7T0KRV8f5g3SfxglMgxiAw8C8LhvHEBUHws=~1; ak_bmsc=7CDBDE1082F50A9D6821A7BB5224859A~000000000000000000000000000000~YAAQe+kyFyMLzBqKAQAA/Ap5HxSQtJ7VxVO2me6qYtIu6NDLoyecsXHuFqIqySewsgfYHoPxPeqLBVj5kAlle0mgUef/xq+CLopHUEW9p+AzER3RkLaQ4NjqWirinVWS87HUf3Zf7W27p1JNEYDMJlvxlUUkwvtP9VrxnGwDSPHMZNOP4j3woLFcZ8bLVXO6DiJpTFCKh9NZibpDoORPBN2V9sUD2ROpsn1dedllExyclHXUQcBJLyVI2+bra2LhhJ2xUkr6EhTQEHhQSCBaoX05PWvj6zWsWCT0P0lSVb0xg0Ws5SMQ7bwYQKGkAohOQaj+0VpHTepQ14fKEld6HS0PhbrzliifrA5n+mKXSoNrMZxUtvbyZwvTkaH+9WsRDZZAmU+hOU3TZGtkw2pyqN4MTVP50g3PYb4k7L0ikU7V6w==; AID=wmlspartner%3D0%3Areflectorid%3D0000000000000000000000%3Alastupd%3D1692745546824; auth=MTAyOTYyMDE4eUAXIFI6Sw4FpUWJJoH%2B8eV5hd9erHwNFFIKmKlrxaMMTjX%2FvRNKO7ceEPF%2Fs74tND0f34MSvtpNu9h1BPZJytfGXWdEY%2F24RTdMylPqkvhvmJGVGaqwo%2BHDx6bZQptJEk8ozGbo5MEn1vkTvRAX7TQK%2FPLfNIdTFiqdtUUpYSMMMu6knZUQlzllkcysFthHMv4QlSFbo12DPRyePNINgTWK8DRV7WegEDnNeeLB8fEH8LTIl0qGI2dEEKS0tcdL8ZCNeaOqne%2Bj6I6LsHEg77hxjz3OdLmjRNKrHIOQEeFeRoCwm%2B4jFEeeD4Ns2SS7yu8uJyVSirjT90HNQKRNZxRuDPcH981%2FwWzF47QuvXj%2FEM7LFEQuZEFpXKC0fRzJVFvbWCsMx0p0u92Ov2Kkopacwyh4jmkr9TcCIXD4RZk%3D; _tsc=MTQyODYyMDIySvOCiRvuw33jOjNtdUQvSPVgPMoFgaEeNI552p9NvmsLtN3GmlgsIO%2BBWsDA4ap1DjNhzd9qwIyO60f9BdpJkepPgTnjE5vz2gqi1WYikHg%2BQAO9KC1zBfReKA6y5wDtqdTCBARdk6YTAR4%2FpKrXzmqWBvRraicutYqnqiDnpRBPnCbJpiAFUgcDWAES4lbhjB3nCj%2BPiMBykpN3j8PGYYcN%2B0JEUxzHMC%2BuMMtiS%2BrdTSUv%2F3AtZJt3%2FthRrYdJLFKmUsi1PvaHRWBuK4z3cr8Tz%2BwVRFb1hfzzV%2B34sLjyx3EVgkR4HtNkZ%2FIhB0QcEnpcbYs2riNa3j5%2BeqsrN%2BLWdfb5LtjZXn%2BWRO3S9ot9t%2BBueu%2FbZRj6D4aAOENpi8rHYsqhAtMb6RH6mKq36ORb7lKDoGNTr6zXGCbMXbBtsCNg4RA88CCcdFUsV7EdMgBM6Q%3D%3D; akavpau_p2=1692746176~id=6d8324129f36861345c329d3a903836a; xptwj=qq:35232bd08eb4d94b5417:YkJK1G7+j5Zx4DFaCtblu1t/N8ttBXUBWmyd3FVJgHkKo93/U1Jm81kSi6bHMuzYj2Q9l9rKudkz7uYxhfMjifn0/DJEx/XYwftIWqpaQ0nvWXEUEH9Bm1szjTyhaSbcbxYhu+9vvvnAl8KJz3KHDurW+tl7NGiYbfRuDItdVRfhWsEZsOwnDt/6jODcwn9DAnXUP4TZ6NvEYdrXIA==; _lat=8c0a8aef10e4fba55c66a49ee002c84bmyacc; com.wm.reflector="reflectorid:22222222227000000000@lastupd:1692746203000@firstcreate:1689551603715"; xptwg=963154313:1E7AC425BD6C3F0:4D55C90:53ECB6D1:869080F1:52C9C580:; TS012768cf=0119e1d2df61722ff2d07d837c0663efe874e279a6012c8d48bdd6eb3dd68c8bad85967a94db6c083744b5b52eceeac87ce82d0974; TS01a90220=0119e1d2df61722ff2d07d837c0663efe874e279a6012c8d48bdd6eb3dd68c8bad85967a94db6c083744b5b52eceeac87ce82d0974; TS2a5e0c5c027=08e19f9f02ab200075dc7a1e384c25407ec50ef9a9c446b21d1e128b1bfcfc12780097580b2dce6c08583454bb1130000896f1bb916c7c90bb2dc346413e992b4e67e93c26e0c4d7f41ff4544b0058f7a9e456697de3b22090b6d3909a3fe055; SPID=6a46803893dab7859a96a6ee2f9de244eb6fa2940613a63441edc2b7169a539eb3caba7e08d5691513e2ad39a772ca58myacc; TS01a90220=01aed3d184696232bc3989da480ca3c2f3e1663d2f2ebc4f66586672ffba03725e28884d852a75572dd5be461a1a7792398973d61f; _lat=606619212d0b163ac9298fae0f52631fwmjet; _m=9; auth=MTAyOTYyMDE4eUAXIFI6Sw4FpUWJJoH%2B8eV5hd9erHwNFFIKmKlrxaMMTjX%2FvRNKO7ceEPF%2Fs74tND0f34MSvtpNu9h1BPZJytfGXWdEY%2F24RTdMylPqkvhvmJGVGaqwo%2BHDx6bZQptJEk8ozGbo5MEn1vkTvRAX7TQK%2FPLfNIdTFiqdtUUpYSMMMu6knZUQlzllkcysFthHMv4QlSFbo12DPRyePNINgTWK8DRV7WegEDnNeeLB8fEH8LTIl0qGI2dEEKS0tcdL8ZCNeaOqne%2Bj6I6LsHEg77hxjz3OdLmjRNKrHIOQEeFeRoCwm%2B4jFEeeD4Ns2SS7yu8uJyVSirjT90HNQKRNZxRuDPcH981%2FwWzF47QuvXj%2FEM7LFEQuZEFpXKC0fRzJVFvbWCsMx0p0u92Ov2Kkopacwyh4jmkr9TcCIXD4RZk%3D; bstc=ZUqiQB2BO54mt61fQv0-qA; com.wm.reflector="reflectorid:22222222227000000000@lastupd:1692746258000@firstcreate:1689551603715"; exp-ck=1ecvP1BukPC1CfYKc1Erqn51IXu7U1KkThS1KvYZX1MhYKp1N6Yhp2NZCJq1PgE9q5R2vTN1R5ktD2SETkS1TIE1G1VxdQI1YnYws4Zmyul1dDqiD1dPmpl2h9ALg3kQp842kylfG1m2Cb11mC9MV2mG0oX2r_-Ov1t_VGX1; mobileweb=0; vtc=brnh2zjPPKKKGrjlvK-guE; xpa=-5XLL|1ecvP|200gl|2c-Ep|5vEu-|8Xuun|8nAQE|Aj49u|BukPC|C2mbG|CfYKc|Cykgk|Erqn5|G-Rah|I02NK|IXu7U|Jc18f|KkThS|KvYZX|MhYKp|N6Yhp|NZCJq|PgE9q|R2vTN|R5ktD|SETkS|Svv7-|TIE1G|VCOYl|VxdQI|X78hm|YdknO|YnYws|ZMf5y|Zmyul|_4HRC|b8OpP|dDqiD|dPmpl|dayNl|h9ALg|kQp84|kylfG|m2Cb1|mC9MV|mG0oX|oZEGf|r_-Ov|t_VGX|xFt_7; xpm=1%2B1692744540%2Bbrnh2zjPPKKKGrjlvK-guE~b56f4f2c-4c29-448b-bd91-dd6551ab843c%2B0; xptc=assortmentStoreId%2B{currentstoreid}; xpth=x-o-mart%2BB2C~x-o-mverified%2Bfalse; xptwg=3580023652:205A306B2B189C0:521636B:70AB9121:DAB83C13:FA800E51:; xptwj=qq:5155573e21eba9fa55ca:1BqLMrvlp9/E6GAyvdlPP91NF+KJ4zwuqWXQEXqTgreO6+XmPsLxXtVoU1Rtjjoy31bwhYiTOwipvl6RJnuBV9QJ5kVmLXijT+s7pW/Pxbel9wCsAzIIuZed8koaCR5Lkn8enqp8jZCpacydGBxve8GRGdteKZVeYradrXz76VTFI+JAdQ3Hv+uvcrqFQ5A+H2bCDZGz1JW3RPRnhQ==; TS012768cf=01aed3d184696232bc3989da480ca3c2f3e1663d2f2ebc4f66586672ffba03725e28884d852a75572dd5be461a1a7792398973d61f; TS2a5e0c5c027=08f5e55f05ab20000c912436c236532b3ab624482707889f246af4813192b71db485b04d6bb76420081a8eee7411300047e5b07d1335d63fce9065c431b3aff517ceba983a177ec282b451bca883c7e7f16c0ef0de08477642e8044d27b2c588; abqme=false; akavpau_p2=1692746858~id=ee38d0b828f5e45a423c3c3b63bdabfc',
            'device_profile_ref_id': 'pskwrbmx2zvcyu9uverorwlf-8qzc0tbvom5',
            'referer': f'https://www.walmart.com/search?q={searchquery}',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'traceparent': '00-21beb0096a9764e5f35b35e55188fa13-14a8b41187f30b55-00',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'wm_mp': 'true',
            'wm_page_url': f'https://www.walmart.com/search?q={searchquery}',
            'wm_qos.correlation_id': 'ycihjDqCvDSa-SfEmzRy_2oMgKAzMiJTQD7o',
            'x-apollo-operation-name': 'Search',
            'x-enable-server-timing': '1',
            'x-latency-trace': '1',
            'x-o-bu': 'WALMART-US',
            'x-o-ccm': 'server',
            'x-o-correlation-id': 'ycihjDqCvDSa-SfEmzRy_2oMgKAzMiJTQD7o',
            'x-o-gql-query': 'query Search',
            'x-o-mart': 'B2C',
            'x-o-platform': 'rweb',
            'x-o-platform-version': 'main-1.95.0-9f8acf-0819T1541',
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
