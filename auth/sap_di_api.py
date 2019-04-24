import requests
from auth.sap_auth import SAPAuth

token = SAPAuth.get_token()

# get SAP company info
url = 'https://thirty48.mynetgear.com/v1/info'
url = 'http://SAPAPI:5000/v1/info'
headers = {"authorization": "JWT " + token, "content-type": "application/json"}
print(headers)

r = requests.get(url, headers=headers)
print(r.text)