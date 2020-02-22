import requests
import json
from datetime import date, datetime, timedelta
from pytz import timezone
from decimal import Decimal
from config import *
from auth.sap_auth import SAPAuth
import shopify


def import_sales_orders():
    API_KEY = '6be780b4e74d0b0c7fa1010878f652e0'
    PASSWORD = '4fcf453158a2c18929ef92ce4cb8c4f0'
    API_VERSION = '2019-07'
    shop_url = "https://thirty-48.myshopify.com/admin"
    shopify.ShopifyResource.set_user(API_KEY)
    shopify.ShopifyResource.set_password(PASSWORD)
    shopify.ShopifyResource.set_site(shop_url)

    shop_orders = []

    # Get recent Shopify orders
    lookup_datetime = timezone('US/Pacific').localize(datetime.now() - timedelta(days=5)).replace(microsecond=0)
    lookup_datetime = lookup_datetime.isoformat()
    shop_orders = get_all_resources(shopify.Order, updated_at_min=lookup_datetime, status='any')

    if shop_orders:
        for order in shop_orders:
            order_attributes = {}
            sap_error = False
            shop_id = ''
            order_date = ''

            order_attributes = order.attributes
            shop_id = str(order_attributes['id'])
            sap_error, sap_fk = IsImported(shop_id)
                  
            if sap_error is False and sap_fk is False and order_attributes['closed_at'] and order_attributes['fulfillment_status'] == 'fulfilled':
                print('New order found, order id: ' + shop_id)
                order_date = order_attributes['created_at'][:10]
                order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
                order_bill_address = {}
                order_ship_address = {}
                order_items_list = []
                tax_code = '0'

                sap_order = {}
                sap_order['Lines'] = []
                sap_order['Expenses'] = []

                sap_order['CardCode'] = 'T481995'
                # sap_order['CardName'] = order['member_name']
                sap_order['NumAtCard'] = str(order_attributes['order_number'])
                sap_order['DocDate'] = order_attributes['created_at'][:10]
                sap_order['DocDueDate'] = order_attributes['created_at'][:10]
                sap_order['TaxDate'] = order_attributes['created_at'][:10]
                sap_order['PickRemark'] = str(order_attributes['id'])
                sap_order['DocTotal'] = float(order_attributes['total_price'])

                # sap_order[''] = order['coupon_discount']
                # sap_order[''] = order['product_total']
                # sap_order[''] = order['shipping_charge']
                # print(order['tax'])
                # sap_order['VatPercent'] = 7.00
                # sap_order['DocTotal'] = order['grand_total']
                sap_order['Comments'] = order_attributes['note'] if order_attributes['note'] else ''
                # sap_order[''] = order['tracking_number']

                # order_bill_address = order['bill_address']
                # order_ship_address = order['ship_address']

                list_index = 0
                line_items = order_attributes['line_items']
                for line_item in line_items:
                    line_item_attributes = line_item.attributes
                    sap_order['Lines'].insert(list_index, {
                        'ItemCode': line_item_attributes['sku'],
                        'Quantity': line_item_attributes['quantity'],
                        'Price': line_item_attributes['price'],
                        'TaxLiable': 0,
                        'TaxCode': tax_code,
                        # 'TaxPercentagePerRow': tax_percent,
                        'DiscountPercent': 0
                    })
                    list_index = list_index + 1
                    print('Item Loop')

                if order_attributes['total_tax'] != '0.00':
                    sap_order['Lines'].insert(list_index, {
                        'ItemCode': 'Tax',
                        'Quantity': 1,
                        'Price': order_attributes['total_tax'],
                        'TaxCode': tax_code,
                        'DiscountPercent': 0
                    })
                    list_index = list_index + 1
                    print('Tax Loop')

                list_index = 0
                shipping_lines = order_attributes['shipping_lines']
                for shipping_line in shipping_lines:
                    shipping_line_attributes = shipping_line.attributes
                    if shipping_line_attributes['price'] != '0.00':
                        sap_order['Expenses'].insert(list_index, {
                            'ExpenseCode': 3,
                            'LineTotal': shipping_line_attributes['price'],
                            'TaxCode': tax_code
                        })
                        list_index = list_index + 1
                        print('Shipping Loop')

                print(sap_order)
                sap_json = json.dumps(sap_order)
                url = sap_url + '/v1/orders'
                token = SAPAuth.get_token()
                if token:
                    headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
                    r = requests.post(url, sap_json, headers=headers)
                    print(r.status_code)
                    print('Line Loop')
            # print('Order Loop')
        print('A')


def get_all_resources(resource, **kwargs):
    resource_count = resource.count(**kwargs)
    resources = []
    if resource_count > 0:
        for page in range(1, ((resource_count-1) // 250) + 2):
            kwargs.update({"limit": 250, "page": page})
            resources.extend(resource.find(**kwargs))
    return resources


def IsImported(shop_id):
    print('Checking if Shopify order is imported')
    sap_error = False
    is_imported = False
    order_located = ''
    
    url = sap_url + '/v1/orders?num=1'
    token = SAPAuth.get_token()
    if token:
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        data = {"columns": ["PickRmrk"],
                "params": {"CardCode": {"op": "=", "value": "T481995"}, "PickRmrk": {"op": "=", "value": shop_id}},
                "LineColumns": ["LineNum", "ItemCode", "Price", "Quantity"]}
        data = json.dumps(data)
        # print(data)
        r = requests.get(url, data=data, headers=headers)

        if r.status_code == 200:
            # print(r.text)
            order_located = r.json()
            if order_located:
                is_imported = True

        return sap_error, is_imported


def get_sap_orders_sync(lookup_date):
    print('Getting Shopify IDs from SAP')
    url = sap_url + '/v1/orders'
    token = SAPAuth.get_token()
    if token:
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        data = {"columns": ["PickRmrk"],
                "params": {"CardCode": {"op": "=", "value": "T481995"}, "DocDate": {"op": ">=", "value": lookup_date}},
                "LineColumns": ["LineNum", "ItemCode", "Price", "Quantity"]}
        data = json.dumps(data)
        # print(data)
        r = requests.get(url, data=data, headers=headers)

        if r.status_code == 200:
            # print(r.text)

            sap_orders = []
            shopify_order_ids = []
            sap_orders = r.json()
            for sap_order in sap_orders:
                if sap_order['PickRmrk']:
                    shopify_order_ids.append(int(sap_order['PickRmrk']))

            return shopify_order_ids


if __name__ == '__main__':
    import_sales_orders()
