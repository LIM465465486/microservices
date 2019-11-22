import requests, simplejson

from config import *


class AuthSAP:
    @staticmethod
    def gettoken():
        url = SAP_URL + '/auth'
        headers = {"content-type": "application/json"}
        data = simplejson.dumps({"username": SAP_USERNAME, "password": SAP_PASSWORD})
        try:
            r = requests.post(url, data, headers=headers, verify=False)
            r.raise_for_status()
            result = r.json()
            return result['access_token']
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh)
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt)
        except requests.exceptions.RequestException as err:
            print('Request Exception:', err)
