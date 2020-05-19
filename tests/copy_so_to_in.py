import requests
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from config import *
from auth.sap_auth import SAPAuth
import shopify


def copy_so_to_in():
    api_key = '6be780b4e74d0b0c7fa1010878f652e0'
    api_password = '4fcf453158a2c18929ef92ce4cb8c4f0'
    api_version = '2019-07'
    shop_url = "https://thirty-48.myshopify.com/admin"
    shopify.ShopifyResource.set_user(api_key)
    shopify.ShopifyResource.set_password(api_password)
    shopify.ShopifyResource.set_site(shop_url)

    print('Begin')
    print('Getting open sales orders')

    url = sap_url + '/v1/orders'
    token = SAPAuth.get_token()
    if token:
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        data = {
            "columns": ["CardCode", "CardName", "DocDate", "DocDueDate", "NumAtCard", "PickRmrk", "TaxDate"],
            "params": {"CardCode": {"op": "=", "value": "T481995"}, "DocStatus": {"op": "=", "value": "O"}},
            "LineColumns": ["DocEntry", "LineNum"]}
        data = json.dumps(data)
        # print(data)
        r = requests.get(url, data=data, headers=headers)
        # print(r.text)

        sap_orders = []
        sap_orders = json.loads(r.text)
        # print(type(sap_order_list))
        # print(sap_order_list)

        if sap_orders:
            print('Located open orders')
            print('Check if orders are shipped')
            sap_shopify_ids = set()

            for order in sap_orders:
                if order['PickRmrk']:
                    sap_shopify_id = None
                    shopify_order = None
                    is_shipped = False
                    sap_shopify_id = int(order['PickRmrk'])
                    shopify_order = shopify.Order.find(sap_shopify_id)
                    if shopify_order:
                        shopify_attributes = {}
                        shopify_attributes = shopify_order.attributes
                        if shopify_attributes['closed_at'] and shopify_attributes['fulfillment_status'] == 'fulfilled':
                            is_shipped = True
                            print('Order shipped: ' + str(sap_shopify_id))
                            print('Copying to IN')
                            sap_invoice = {}
                            sap_invoice['Lines'] = []
                            sap_invoice['Expenses'] = []

                            # print(order['order_number'])
                            sap_invoice['CardCode'] = order['CardCode']
                            sap_invoice['CardName'] = order['CardName']
                            sap_invoice['DocDate'] = order['DocDate']
                            sap_invoice['DocDueDate'] = order['DocDueDate']
                            sap_invoice['NumAtCard'] = order['NumAtCard']
                            sap_invoice['PickRmrk'] = order['PickRmrk']
                            sap_invoice['TaxDate'] = order['TaxDate']

                            line_index = 0
                            for line in order['Lines']:
                                sap_invoice['Lines'].insert(
                                    line_index, {
                                        'BaseType': '17',
                                        'BaseEntry': int(line['DocEntry']),
                                        'BaseLine': int(line['LineNum'])
                                    }
                                )
                                line_index += 1

                            expense_index = 0
                            for expense in order['Expenses']:
                                sap_invoice['Expenses'].insert(
                                    expense_index, {
                                        'BaseDocType': '17',
                                        'BaseDocEntry': int(expense['DocEntry']),
                                        'BaseDocLine': int(expense['LineNum'])
                                    }
                                )
                                expense_index += 1





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
            print('Web API offline or no open orders')

        print('End')


if __name__ == '__main__':
    copy_so_to_in()
