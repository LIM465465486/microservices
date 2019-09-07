import requests
import json
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
    sap_orders = []
    since_id = get_sap_since_id()
    # Get the current shop
    orders = get_all_resources(shopify.Order, since_id=since_id, status='any')
    print('A')


def get_all_resources(resource, **kwargs):
    resource_count = resource.count(**kwargs)
    resources = []
    if resource_count > 0:
        for page in range(1, ((resource_count-1) // 250) + 2):
            kwargs.update({"limit": 250, "page": page})
            resources.extend(resource.find(**kwargs))
    return resources


def get_sap_since_id():
    print('Getting SAP since ID')
    url = sap_url + '/v1/orders'
    token = SAPAuth.get_token()
    headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
    data = {"columns": ["PickRmrk"],
            "params": {"CardCode": {"op": "=", "value": "T481995"}, "DocDate": {"op": ">=", "value": "2019-8-15"}}, "LineColumns": ["LineNum", "ItemCode", "Price", "Quantity"]}
    data = json.dumps(data)
    # print(data)
    r = requests.get(url, data=data, headers=headers)
    # print(r.text)

    sap_orders = []
    shopify_order_ids = []
    sap_orders = json.loads(r.text)
    for sap_order in sap_orders:
        if sap_order['PickRmrk']:
            shopify_order_ids.append(int(sap_order['PickRmrk']))
    since_id = max(shopify_order_ids)

    return since_id


if __name__ == '__main__':
    import_sales_orders()
