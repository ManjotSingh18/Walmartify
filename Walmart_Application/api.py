from abc import ABC, abstractmethod
import urllib, json
import base64

#Reversion
class WEBAPI(ABC):
#Parent function that encompasses urls and retrieves data from APIs that respond in Json wrapped data
    def _download_url(self, url_to_download: str) -> dict:
        try:
            response = None
            r_obj = None
            response = urllib.request.urlopen(url_to_download)
            json_results = response.read()
            r_obj = json.loads(json_results)
# Describes Error Codes that occur with HTTP
        except urllib.error.HTTPError as e:
            print('Failed to download contents of URL')
            print('Status code: {}'.format(e.code))
            if e.code == 401:
                print("Unauthorized Error")
            elif e.code == 400:
                print("Bad Request, Invalid Syntax")
            elif e.code == 403:
                print("Forbidden, protected by server")
            elif e.code == 404:
                print("Not Found, resource not avalible")
            elif e.code == 500:
                print("Internal Server Error")
            elif e.code == 504:
                print("Server was unable to respond in given time")
        finally:
            if response != None:
                response.close()
        return r_obj
#Requires specific APIKEY to be given from user to sucsessfuly utlize specific API 	
def set_apikey(self, apikey:str) -> None:
    self.Apikey=apikey
#These are parent methods that will be used later on by the child
@abstractmethod
def load_data(self):
    pass

