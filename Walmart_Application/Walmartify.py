from API_Template import WEBAPI
import geocoder
import json
import requests
import re
import bs4 as B
#Locator API
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
        for stores in data['results']:
            self.stores.append((stores['poi']['name'],(stores['poi']['url'], stores['address']['freeformAddress'])))

#Main Application
class MainApplication:
    def __init__(self):
        storequery='Walmart'
        searchquery=str(input('\nSearch: '))
        if searchquery == 'Q':
            quit()
        filterquery=str(input('Filter Keyword: '))
        if filterquery=='' or filterquery ==' ':
            filterquery=None
        #CurrentLocation [Lat, Long] prodcut of gecoder.ip method
        cl = geocoder.ip('me')
        locator=LocatorApi(cl.lat,cl.lng,storequery)
        locator.load_data()
        self.SS(locator, searchquery, filterquery)
    #StoreSorter
    def SS(self, locator, search, filtero,store={}):
        store[locator.storequery.lower()] = locator.stores
        WalmartScraper(search,filtero, store[locator.storequery.lower()])
#Walmart Scraper
class WalmartScraper:
    def __init__(self, searchquery=None, filterquery=None, walmartstores=None):
        for walmart in walmartstores:
            currenturl=walmart[1][0]
            id_=re.compile(r'\d\d\d\d')
            currentlocation=walmart[1][1]
            try:
                currentstoreid=id_.search(currenturl).group()
                currentzipcode=walmart[1][1].split(' ')[-1]
                currentstatecode=walmart[1][1].split(' ')[-2]
                print('\n'+currentlocation+'\n')
                print('Product | Gas | Total\n' )
            except:
                pass

            
            url = f"https://www.walmart.com/store/electrode/api/search?query={searchquery}&stores={currentstoreid}&cat_id=0&ps=24&offset=0&prg=desktop&zipcode={currentzipcode}&stateOrProvinceCode={currentstatecode}"

            headers = {
              'authority': 'www.walmart.com',
              'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
              'sec-ch-ua-mobile': '?0',
              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
              'sec-ch-ua-platform': '"Windows"',
              'content-type': 'application/json',
              'accept': '*/*',
              'sec-fetch-site': 'same-origin',
              'sec-fetch-mode': 'cors',
              'sec-fetch-dest': 'empty',
              'referer': f'{currenturl}',
              'accept-language': 'en-US,en;q=0.9',
              'cookie': 'adblocked=false; ACID=3c12e216-9952-42a1-8694-9fb9102da2c3; hasACID=true; vtc=T5RYQZf-Llt2v2RaDuVh24; _pxvid=e885bb5d-4d75-11ec-8e14-794a4f4d5369; TBV=7; hasLocData=1; _pxhd=KE55Guw-3PD0xP207jfZgYi6dRROA9/wyoC5Zz6abGzUngIzyntpwlSWkhTmNaPg2ux6Z5fDsY6n13WqgOCYzg==:CTdfnhqCFLkPvoQlzaxUbMlRUk8Et0fAQfeETkDRkNUyjXr1lbHR-xjgWaTZKLnrZc2pbeG9hMMzdDydfyeNeG3Rr8IAuM80sfapOwU2cs0=; tb_sw_supported=true; assortmentStoreId=5192; adblocked=false; DL=95843%2C%2C%2Cip%2C95843%2C%2C; __gads=ID=b7e8aa9ee6ce8ebf:T=1640159399:S=ALNI_ManaVld9br0czUyBNUOGDLg2jfzNg; _gcl_au=1.1.1969812634.1640159399; locGuestData=eyJpbnRlbnQiOiJTSElQUElORyIsInN0b3JlSW50ZW50IjoiUElDS1VQIiwibWVyZ2VGbGFnIjp0cnVlLCJwaWNrdXAiOnsibm9kZUlkIjoiNTE5MiIsInRpbWVzdGFtcCI6MTYzOTk4Mjg1NDM2M30sInBvc3RhbENvZGUiOnsidGltZXN0YW1wIjoxNjM5OTgyODU0MzYzLCJiYXNlIjoiOTU4NDMifSwidmFsaWRhdGVLZXkiOiJwcm9kOnYyOjNjMTJlMjE2LTk5NTItNDJhMS04Njk0LTlmYjkxMDJkYTJjMyJ9; TB_Latency_Tracker_100=1; TB_Navigation_Preload_01=1; TB_SFOU-100=1; location-data=95843%3AAntelope%3ACA%3A%3A1%3A1|408%3B%3B1.68%2C1g9%3B%3B1.88%2C2v4%3B%3B3.9%2C4m5%3B%3B4.08%2C3e1%3B%3B4.72%2C3o7%3B%3B5.4%2C38q%3B%3B5.98%2C1j8%3B%3B6.3%2C4m6%3B%3B7.09%2C4m4%3B%3B7.52||6|1|1xle%3B16%3B10%3B11.16%2C1xlk%3B16%3B11%3B11.61%2C1xj6%3B16%3B12%3B11.72%2C1xkz%3B16%3B13%3B14.17%2C1yff%3B16%3B14%3B14.89; bstc=c0pe_41V8PblmSwADFHn_E; mobileweb=0; xpa=CfaEu|OHKN-|s6z_-; exp-ck=CfaEu1; bm_mi=97387E23FF47073211246E54CBECBD18~t5nNpC0h++NYf7KiGrZ8cYm8H0Na2+x/e3ZGcknwbCDDzKFHkYd1btpq4yPkzMfBU+AAUapbeYtoGDZbvqPq+Cz3Q0ch22lCnb6Som5v/vCNxCQdLGmReAHrtXc/sbt9i5RDxkYiqPhEraboWH3LRdPdNopsUJBxD5DYZfjq1u7q/I6GpnP7jGz2kJPrOymKrLN0KWA2no3Sl4H+isObPXjF7YCXB+j6CvE0kwAER7HgS8aTpkqQYbflViUhncIWn63G1XuSUCW8RDhspyZ0eQ==; s_pers_2=om_mv3d%3D%3Aadid-%3Asourceid-%3Awmls-%3Acn-Tracking_local_pack_1%7C1640586281276%3B+om_mv7d%3D%3Aadid-%3Asourceid-%3Awmls-%3Acn-Tracking_local_pack_1%7C1640931881276%3B+om_mv14d%3D%3Aadid-%3Asourceid-%3Awmls-%3Acn-Tracking_local_pack_1%7C1641536681277%3B+om_mv30d%3D%3Aadid-%3Asourceid-%3Awmls-%3Acn-Tracking_local_pack_1%7C1642919081277%3BuseVTC%3DY%7C1703438681; pxcts=cc06c960-6479-11ec-952b-3372d946dc0d; xpm=1%2B1640323480%2BT5RYQZf-Llt2v2RaDuVh24~%2B0; ak_bmsc=96BB808B7A342DBC179DF7913CB7EF48~000000000000000000000000000000~YAAQdMcbuCKpNbR9AQAABArm6g4WXimg8IRDp5pFjdAKIpEtaFtrde1hlwiDq5dr8iWr4MfQiSFbexOMf3kgWaciTxH+J2VxSsPJJQcN6NqjglJbGCExDbOA0F8+d2NBoT7Nhgi5ln1qYQHO8LvcXQghPm8P3L7k+Kk3OuxPP9pEjnIwcdjzziD060cn6X+1aJf1fNlEwyREoEmXherZrH25PZ0rQTLUvJ8bx6aO8r558lsXwPLvXJcSPhO/oGnbLoMq+HAR/ASgrQBJF+FvXtCSzAIf9YwsRFY2w1xi8aIf8d1+HxnaDfpCBSRDT9JWQMioKNGhC7eQGxwFe3T9RG7fOfYIMguhkXI3P9U/CRFiC3wvfsoeKw57PDRsUstJFuGnDtU+nXP8crGrCnar+V4fgGi3MnsA+I7URb4SbWCwXQ3VOQ1PskWQZgiR9/QoB3v3OtYyuNbKJhyIG819sk6dLHx5Wkt2lkQu8n02iJoh7Wd8SgPE3rUBfaZUYO9ZVM1CmMqEqVIKEvZZMxQCu1FcsEWMoei4nvfIVE+9ZFJvHPzJELtpOQrTtw==; crumb=2W8s6pHOe9kY7rKdvhaztqXEhMOjYqlHC0148smLLSg; AID=wmlspartner%253Dwmtlabs%253Areflectorid%253D22222222220451109050%253Alastupd%253D1640324323282; auth=MTAyOTYyMDE4sy1oIjxY%2F0heUpQTJKQNmhVNI60nCW1ItcKJ6KjUJ73cniU3zGVrgPiO6JGby4WwtfMES8Cc9IJVvwYod3vPcaW2U4ObyAFIaO0wL2JTSAPIBMvXjCoAyoXKuOrzsuUm767wuZloTfhm7Wk2Kcjygv3M5Jnvc7ePkiG6%2BkglNADFdLjTXvng%2B0hLan5n7g0Mv6p66aaWkw%2F60xaJCtDX3yxRaDLTHRAwaS0L99kf3QYUMk70P8glgOEpLOprhDfMywI05adPtwc9%2Fm5r1ONHRz3epSCZByfkNnkw50ckIlrrZnJ%2Bgkg%2FUa9YGfltICBOcY0P4kteusqMdjZ3QIkXtS5QTRSujrZc5TWkleIJxhSt0Unb75iXTjaCq6ye3B1y4tVsvoq1jyGsl8mqZCac40jyrOXbKKhH072NS%2FW0j%2FU%3D; locDataV3=eyJpbnRlbnQiOiJTSElQUElORyIsInBpY2t1cCI6W3siYnVJZCI6IjAiLCJub2RlSWQiOiI1MTkyIiwiZGlzcGxheU5hbWUiOiJTYWNyYW1lbnRvIFN1cGVyY2VudGVyIiwibm9kZVR5cGUiOiJTVE9SRSIsImFkZHJlc3MiOnsicG9zdGFsQ29kZSI6Ijk1ODQyIiwiYWRkcmVzc0xpbmUxIjoiNTgyMSBBbnRlbG9wZSBSZCIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnkiOiJVUyIsInBvc3RhbENvZGU5IjoiOTU4NDItMzkwMiJ9LCJnZW9Qb2ludCI6eyJsYXRpdHVkZSI6MzguNzA0MzE4LCJsb25naXR1ZGUiOi0xMjEuMzMxODYxfSwiaXNHbGFzc0VuYWJsZWQiOnRydWUsInNjaGVkdWxlZEVuYWJsZWQiOnRydWUsInVuU2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2V9XSwiZGVsaXZlcnkiOnsiYnVJZCI6IjAiLCJub2RlSWQiOiIxODgxIiwiZGlzcGxheU5hbWUiOiJBbnRlbG9wZSBTdXBlcmNlbnRlciIsIm5vZGVUeXBlIjoiU1RPUkUiLCJhZGRyZXNzIjp7InBvc3RhbENvZGUiOiI5NTg0MyIsImFkZHJlc3NMaW5lMSI6Ijc5MDEgV2F0dCBBdmUiLCJjaXR5IjoiQW50ZWxvcGUiLCJzdGF0ZSI6IkNBIiwiY291bnRyeSI6IlVTIiwicG9zdGFsQ29kZTkiOiI5NTg0My0yMDI1In0sImdlb1BvaW50Ijp7ImxhdGl0dWRlIjozOC43MTI4NDIsImxvbmdpdHVkZSI6LTEyMS4zOTQ2MDh9LCJpc0dsYXNzRW5hYmxlZCI6dHJ1ZSwic2NoZWR1bGVkRW5hYmxlZCI6dHJ1ZSwidW5TY2hlZHVsZWRFbmFibGVkIjpmYWxzZSwiYWNjZXNzUG9pbnRzIjpbeyJhY2Nlc3NUeXBlIjoiREVMSVZFUllfQUREUkVTUyJ9XX0sInNoaXBwaW5nQWRkcmVzcyI6eyJsYXRpdHVkZSI6MzguNzE1MywibG9uZ2l0dWRlIjotMTIxLjM2NTMsInBvc3RhbENvZGUiOiI5NTg0MyIsImNpdHkiOiJBbnRlbG9wZSIsInN0YXRlIjoiQ0EiLCJjb3VudHJ5Q29kZSI6IlVTQSIsImdpZnRBZGRyZXNzIjpmYWxzZX0sImFzc29ydG1lbnQiOnsibm9kZUlkIjoiNTE5MiIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImFjY2Vzc1BvaW50cyI6bnVsbCwiaW50ZW50IjoiUElDS1VQIiwic2NoZWR1bGVFbmFibGVkIjpmYWxzZX0sImluc3RvcmUiOmZhbHNlLCJyZWZyZXNoQXQiOjE2NDAzNDU5MjMzODIsInZhbGlkYXRlS2V5IjoicHJvZDp2MjozYzEyZTIxNi05OTUyLTQyYTEtODY5NC05ZmI5MTAyZGEyYzMifQ%3D%3D; akavpau_p2=1640324923~id=39107fa4a6832fdec2493280003a40ab; com.wm.reflector="reflectorid:22222222220451109050@lastupd:1640324324000@firstcreate:1637792934968"; TS013ed49a=01538efd7ce3dd70b2fd01411e161a1ca3f4010d0bce805fefc9f668ac09980ad7afd83ff0808864e258eccad731e84e586a4c1532; wm_client_ip=67.181.236.210; _uetsid=c35e72a062fb11ec8e2203b1a0eac947; _uetvid=c35ebd5062fb11ec9a4709cd43236fe6; _pxde=cdaee3f5440ac728746e33f3250d25f43394aeaf7ad78a47acbae44b895ef631:eyJ0aW1lc3RhbXAiOjE2NDAzMjQ4NDE1MDYsImZfa2IiOjAsImlwY19pZCI6W119; TS01b0be75=01538efd7cff8f7c66c49baa53d2f2fa0056c045bc36a9721e2ee02bcacc0343af77cf35dd06968d2223c00636197f85bf8fa60a3e; next-day=1640361600|true|false|1640606400|1640325015; xptwg=1065397656:1EC181E442873B0:5087B48:86B3982B:B34F3060:1076D21C:; bm_sv=162EA12308C917B6BC22A4749EB3135B~C+N9QUrx+udvzKIEZxdTTm9V5jo46glR6jnyNAe0QVZEceTVEWqG+nK9VJMdWIfdGx1IIXN01a9DB+BHw6E3tXPGL12aBl5N2AZHRUBrwvOswycp9M+RoHFM7FsXHGFbZhIT3X26EfiWGJJrK0fWIPm/z0obHLyCSOF6aWZaNYY=; vtc=T5RYQZf-Llt2v2RaDuVh24'
            }

            r = requests.request("GET", url, headers=headers)

            data=json.loads(r.text)
            for items in data['itemStacks'][0]['items']:
                try:
                    if filterquery != None:
                        checker=filterquery.split()
                        if len(checker) == 1:
                            if checker[0].lower() in items['title'].lower():
                                print("%-25s"%str((str(items['primaryOffer']['offerPrice'])+' '+items['title'])))
                        else:
                            comp=any([True if stuff.lower() in items['title'].lower() else False for stuff in checker])
                            if comp:
                                print("%-25s"%str((str(items['primaryOffer']['offerPrice'])+' '+ items['title'])))
    
                    else:
                        print("%-25s"%str((str(items['primaryOffer']['offerPrice'])+ ' '+items['title'])))
                except KeyError:
                    print(items['title'], 'No Offer Found')
 
if __name__=='__main__':
    while True:
        MainApplication()
