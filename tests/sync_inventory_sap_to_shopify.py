import requests
import json
from decimal import Decimal
from config import *
from auth.sap_auth import SAPAuth
import shopify


def sync_inventory():
    API_KEY = '6be780b4e74d0b0c7fa1010878f652e0'
    PASSWORD = '4fcf453158a2c18929ef92ce4cb8c4f0'
    API_VERSION = '2019-07'
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
                inventory_item_id=variant_attributes['inventory_item_id'],
                inventory_quantity=variant_attributes['inventory_quantity']
            ))

    header = ['product_id', 'variant_id', 'sku', 'inventory_item_id', 'inventory_quantity']
    file_name = 'shop_export'
    # export_dict(file_name=file_name, header=header, dict_data=shop_products)

    sap_items = get_sap_items()

    if not sap_items:
        print('Error: No response from SAP')
        return

    for sap_item in sap_items:
        item_code = sap_item['ItemCode']
        quantity = int(sap_item['Warehouses'][0]['Available'])
        sap_products.append(dict(item_code=item_code, quantity=quantity))

    header = ['item_code', 'quantity']
    file_name = 'sap_export'
    # export_dict(file_name=file_name, header=header, dict_data=sap_products)

    # inventory location number 18867912807
    # shopify.InventoryLevel.set(location_id=18867912807, inventory_item_id=808950810, available=10)

    for shop_product in shop_products:
        # print(shop_product)
        for sap_product in sap_products:
            # print(sap_product)
            if shop_product['sku'] == sap_product['item_code'] and shop_product['inventory_quantity'] != sap_product['quantity']:
                print(shop_product)
                print(sap_product)

                update_quantity = sap_product['quantity']
                inventory_levels = shopify.InventoryLevel.find(location_id=18867912807, inventory_item_ids=shop_product['inventory_item_id'])
                for inventory_level in inventory_levels:
                    inventory_level.set(
                        location_id=18867912807,
                        inventory_item_id=shop_product['inventory_item_id'],
                        available=update_quantity)
                break


def get_all_resources(resource, **kwargs):
    resource_count = resource.count(**kwargs)
    resources = []
    if resource_count > 0:
        for page in range(1, ((resource_count-1) // 250) + 2):
            kwargs.update({"limit": 250, "page": page})
            resources.extend(resource.find(**kwargs))
    return resources


def get_sap_items():
    print('Getting SAP products')
    url = sap_url + '/v1/items'
    token = SAPAuth.get_token()
    if token:
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        data = {"columns": ["ItemCode"],
                "params": {}
                }
        data = json.dumps(data)
        # print(data)
        r = requests.get(url, data=data, headers=headers)
        # print(r.text)

        sap_items = []
        sap_items = json.loads(r.text)
        # print(type(sap_products_list))
        # print(sap_products_list)
        return sap_items


def export_dict(file_name, header, dict_data):
    import csv
    csv_columns = header
    csv_file = file_name + '.csv'
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")


if __name__ == '__main__':
    sync_inventory()
