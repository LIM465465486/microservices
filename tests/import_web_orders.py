import requests
import json
from config import *
from auth.sap_auth import SAPAuth

web_r = requests.get(web_url + '/order_display/?token=2185CC75&day=15')
# web_r = requests.get(web_url + '/order_display/?token=2185CC75&order_number=T1904_00016_TBHD')
orders_list = []
orders_list = json.loads(web_r.text)
#print(orders_list)

# with open('/home/luis/lim/microservices/tests/web_orders.json') as json_file:
#     data = json.load(json_file)
# orders_list = []
# orders_list = data

url = sap_url + '/v1/orders'
token = SAPAuth.get_token()
headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
data = {"columns": ["NumAtCard"], "params": {"CardCode": {"op": "=", "value": "T481995"}, "DocDate": {"op": ">=", "value": "2019-4-1"}}, "LineColumns": ["LineNum", "ItemCode", "Price", "Quantity"]}
data = json.dumps(data)
# print(data)
r = requests.get(url, data=data, headers=headers)
# print(r.text)

sap_order_list = []
sap_order_list = json.loads(r.text)
# print(type(sap_order_list))
# print(sap_order_list)

clean_list = []
for sap_ref in sap_order_list:
    # print(sap_ref['NumAtCard'])
    clean_list.append(sap_ref['NumAtCard'])

if orders_list:
    for order in orders_list:
        if order['order_number'] not in clean_list and order['order_number'] == 'T1904_00016_TBHD':
            print(order['order_number'])
            order_bill_address = {}
            order_ship_address = {}
            order_items_list = []

            sap_order = {}
            sap_order['Lines'] = []

            # print(order['order_number'])
            sap_order['CardCode'] = 'T481995'
            sap_order['CardName'] = order['member_name']
            sap_order['NumAtCard'] = order['order_number']
            sap_order['DocDate'] = order['dtc'][:10]
            sap_order['DocDueDate'] = order['dtc'][:10]
            sap_order['TaxDate'] = order['dtc'][:10]

            # sap_order[''] = order['coupon_discount']
            # sap_order[''] = order['product_total']
            # sap_order[''] = order['shipping_charge']
            # sap_order[''] = order['tax']
            # sap_order['DocTotal'] = order['grand_total']
            sap_order['Comments'] = order['note']
            # sap_order[''] = order['tracking_number']

            order_bill_address = order['bill_address']
            order_ship_address = order['ship_address']
            order_items_list.append(order['items'])

            order_item = {}
            for order_hold in order_items_list:
                for key, val in order_hold.items():
                    # print(val)
                    order_item = val
                    # print(order_item['model'], order_item['product_type'])
                    list_index = 0
                    if order_item['product_type'] == 'pack':
                        order_item_size = ''
                        if order_item['size'] == 'xs':
                            order_item_size = '0'
                        elif order_item['size'] == 's':
                            order_item_size = '1'
                        elif order_item['size'] == 'm':
                            order_item_size = '2'
                        elif order_item['size'] == 'l':
                            order_item_size = '3'
                        elif order_item['size'] == 'xl':
                            order_item_size = '4'
                        elif order_item['size'] == 'xxl':
                            order_item_size = '5'

                        order_packs = []
                        order_packs = order_item['pack_items']

                        if order_item['model'] == 'RU3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'RU' + order_item_size + order_pack['model'][2:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'RUL3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'RUL' + order_item_size + order_pack['model'][3:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'RUS3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'RUS' + order_item_size + order_pack['model'][3:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'CRU3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'CRU' + order_item_size + order_pack['model'][3:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'CYMIX-3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'CY' + order_item_size + order_pack['model'][2:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'CYMIX2-3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'CY' + order_item_size + order_pack['model'][2:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'HK3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'HK' + order_item_size + order_pack['model'][2:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        if order_item['model'] == 'HKL3PK':
                            for order_pack in order_packs:
                                print(order_item['model'], order_item['size'], order_pack['model'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'HKL' + order_item_size + order_pack['model'][3:],
                                    'Quantity': order_item['quantity'],
                                    'Price': round((float(order_item['unit_price']) / float(order_item['pack_q'])), 2),
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                    if order_item['product_type'] == 'single':
                        if order_item['size'] != 'off':
                            order_item_size = ''
                            if order_item['size'] == 'xs':
                                order_item_size = '0'
                            elif order_item['size'] == 's':
                                order_item_size = '1'
                            elif order_item['size'] == 'm':
                                order_item_size = '2'
                            elif order_item['size'] == 'l':
                                order_item_size = '3'
                            elif order_item['size'] == 'xl':
                                order_item_size = '4'
                            elif order_item['size'] == 'xxl':
                                order_item_size = '5'

                            if order_item['model'] == 'RUSBKG':
                                print(order_item['model'], order_item['size'])
                                print(list_index)
                                sap_order['Lines'].insert(list_index, {
                                    'ItemCode': 'RUS' + order_item_size + order_item['model'][3:],
                                    'Quantity': order_item['quantity'],
                                    'Price': order_item['unit_price'],
                                    'TaxCode': '0',
                                    'DiscountPercent': 0
                                })
                                list_index = list_index + 1

                        else:
                            sap_order['Lines'].insert(list_index, {
                                'ItemCode': order_item['model'],
                                'Quantity': order_item['quantity'],
                                'Price': order_item['unit_price'],
                                'TaxCode': '0',
                                'DiscountPercent': 0
                            })
                            list_index = list_index + 1

                    print('Item Loop')
            print(sap_order)
            sap_json = json.dumps(sap_order)
            url = sap_url + '/v1/orders'
            token = SAPAuth.get_token()
            headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
            r = requests.post(url, sap_json, headers=headers)
            print(r.status_code)
            print(r.text)
        # print('Order Loop')

print('End')

