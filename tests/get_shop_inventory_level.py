import shopify

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
inventory = shopify.InventoryLevel.get()

print(inventory)
