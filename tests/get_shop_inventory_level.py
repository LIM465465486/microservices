import requests
import json
from decimal import Decimal
from config import *
from auth.sap_auth import SAPAuth
import shopify


def get_products():
    API_KEY = '6be780b4e74d0b0c7fa1010878f652e0'
    PASSWORD = '4fcf453158a2c18929ef92ce4cb8c4f0'
    API_VERSION = '2019-07'
    # shop_url = "https://%s:%s@thirty-48.myshopify.com:443/admin/api/%s" % (API_KEY, PASSWORD, API_VERSION)
    # print(shop_url)
    # print('https://6be780b4e74d0b0c7fa1010878f652e0:4fcf453158a2c18929ef92ce4cb8c4f0@thirty-48.myshopify.com/admin/api/2019-07/orders.json')
    # shopify.ShopifyResource.set_site(shop_url)
    shop_url = "https://thirty-48.myshopify.com/admin"
    shopify.ShopifyResource.set_user(API_KEY)
    shopify.ShopifyResource.set_password(PASSWORD)
    shopify.ShopifyResource.set_site(shop_url)

    shop_products = []
    sap_products = []

    # Get the current shop
    products = get_all_resources(shopify.Product)

    for product in products:
        product_variants = []
        product_variants = product.attributes['variants']
        for product_variant in product_variants:
            variant_attributes = {}
            variant_attributes = product_variant.attributes
            # print(variant_attributes['sku'])
            shop_products.append(dict(
                product_id=product.id,
                variant_id=product_variant.id,
                sku=variant_attributes['sku'],
                inventory_item_id=variant_attributes['inventory_item_id']
            ))

    sap_products_list = get_sap_products_list()


def get_all_resources(resource, **kwargs):
    resource_count = resource.count(**kwargs)
    resources = []
    if resource_count > 0:
        for page in range(1, ((resource_count-1) // 250) + 2):
            kwargs.update({"limit": 250, "page": page})
            resources.extend(resource.find(**kwargs))
    return resources


def get_sap_products_list():
    print('Getting SAP products')
    url = sap_url + '/v1/items'
    token = SAPAuth.get_token()
    headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
    data = {"columns": ["ItemCode"],
            "params": {}}
    data = json.dumps(data)
    # print(data)
    r = requests.get(url, data=data, headers=headers)
    # print(r.text)

    sap_products_list = []
    sap_products_list = json.loads(r.text)
    # print(type(sap_products_list))
    # print(sap_products_list)
    return sap_products_list


if __name__ == '__main__':
    get_products()
