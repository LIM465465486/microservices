import requests
import json
from decimal import Decimal
from config import *
from auth.sap_auth import SAPAuth

print('Begin')
print('Getting open sales orders')

url = sap_url + '/v1/orders'
token = SAPAuth.get_token()
headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
data = {"columns": ["CardCode", "CardName", "NumAtCard", "DocDate", "DocDueDate", "TaxDate"], "params": {"CardCode": {"op": "=", "value": "T481995"}, "DocStatus": {"op": "=", "value": "O"}}, "LineColumns": ["DocEntry", "LineNum"]}
data = json.dumps(data)
# print(data)
r = requests.get(url, data=data, headers=headers)
# print(r.text)

sap_order_list = []
sap_order_list = json.loads(r.text)
# print(type(sap_order_list))
# print(sap_order_list)

if sap_order_list:
    print('Copying to IN')
    for order in sap_order_list:
        sap_invoice = {}
        sap_invoice['Lines'] = []
        sap_invoice['Expenses'] = []

        # print(order['order_number'])
        sap_invoice['CardCode'] = order['CardCode']
        sap_invoice['CardName'] = order['CardName']
        sap_invoice['NumAtCard'] = order['NumAtCard']
        sap_invoice['DocDate'] = order['DocDate']
        sap_invoice['DocDueDate'] = order['DocDueDate']
        sap_invoice['TaxDate'] = order['TaxDate']

        list_index = 0

        i = 0
        for line in order['Lines']:
            sap_invoice['Lines'].insert(list_index, {'BaseType': '17', 'BaseEntry': int(line['DocEntry']), 'BaseLine': int(line['LineNum'])})
            list_index = list_index + 1

        print(sap_invoice)
        sap_json = json.dumps(sap_invoice)
        url = sap_url + '/v1/invoices'
        token = SAPAuth.get_token()
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        r = requests.post(url, sap_json, headers=headers)
        print(r.status_code)
        print(r.text)
    # print('Order Loop')
else:
    print('Web API offline or no new orders')

print('End')
