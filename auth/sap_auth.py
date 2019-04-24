import requests
import simplejson


class SAPAuth:
    @staticmethod
    def get_token():
        url = 'https://thirty48.mynetgear.com/auth'
        url = 'http://SAPAPI:5000/auth'
        headers = {"content-type": "application/json"}
        data = simplejson.dumps({"username": "user1", "password": "Tsurhhv8374heuvr4!"})
        try:
            r = requests.post(url, data, headers=headers)
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