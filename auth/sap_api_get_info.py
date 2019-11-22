import requests

from auth.sap_api_get_token import AuthSAP
from config import *

token = AuthSAP.gettoken()

# get SAP company info
url = SAP_URL + '/v1/info'
headers = {"authorization": "JWT " + token, "content-type": "application/json"}
print(headers)

r = requests.get(url, headers=headers, verify=False)
print(r.json)
