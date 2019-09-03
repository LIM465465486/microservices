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


    # Get the current shop
    products = get_all_resources(shopify.Product)

    for product in products:
        product_attributes = {}
        product_variants = []
        product_attributes = product.attributes
        product_variants = product_attributes['variants']
        for item in product_variants:
            variant_attributes = {}
            variant_attributes = item.attributes
            print(variant_attributes['sku'])

        print('A')


def get_all_resources(resource, **kwargs):
    resource_count = resource.count(**kwargs)
    resources = []
    if resource_count > 0:
        for page in range(1, ((resource_count-1) // 250) + 2):
            kwargs.update({"limit": 250, "page": page})
            resources.extend(resource.find(**kwargs))
    return resources


if __name__ == '__main__':
    get_products()
