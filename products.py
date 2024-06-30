import scrapy
import json

class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["www.kingcar.tw"]
    start_urls = ["https://www.kingcar.tw/"]

    def parse(self, response):
      meta = response.meta
      banners = response.css('li[class="dropdown"]')
      for banner in banners:
        if banner.css('a span ::text').get() == '商品分類':
          categories = banner.css('div[class="dropdown-menu"] ul[class="link_shelf_second"] li[class="relative"]')
          for cate in categories:
            meta['cate1Name'] = cate.css('a span ::text').get()
            subcategories = cate.css('ul[class="link_shelf_third"] li')
            for subcate in subcategories:
                meta['cate2Name'] = subcate.css('a span ::text').get()
                meta['cate2Url'] = response.urljoin(subcate.css('a ::attr(href)').get())
                yield scrapy.Request(url=meta['cate2Url'], callback=self.parse_products, meta=meta, dont_filter=True)
          break

    def parse_products(self, response):
        meta = response.meta
        print(response.css('div[class="pagination-container"] * ::text').get())
        products = response.css('div[class="product with_slogan"]')
        for prod in products:
            meta['saleUrl'] = response.urljoin(prod.css('div[class="product_image"] a ::attr(href)').get())
            url = meta['saleUrl'] + '.json'
            yield scrapy.Request(url=url, callback=self.parse_details, meta=meta, dont_filter=True)

    def parse_details(self, response):
        meta = response.meta
        data = json.loads(response.text)
        meta['dealId'] = str(data['id'])
        meta['dealName'] = data['title']
        meta['storingCondition'] = '/'.join(data['temperature_types'])
        meta['saleStartedAt'] = data['sell_from']
        meta['saleEndedAt'] = data['sell_to']
        meta['salePrice'] = data['price']
        meta['mainImgUrl'] = response.urljoin(data['photos'][0]['photo']['product_image_uid'])
        meta['unitsold'] = data['total_sold']
        meta['isSoldout'] = 0 if data['available'] else 1
        variants = data['variants']
        if len(variants) > 0:
            for var in variants:
                meta['optionId'] = str(var['id'])
                meta['optionName'] = var['title']
                meta['skuId'] = var['sku']
                meta['option1'] = var['option1']
                meta['option2'] = var['option2']
                meta['option3'] = var['option3']
                meta['isSoldout'] = 0 if var['available'] else 1
                meta['salePrice'] = var['price']
                meta['marketPrice'] = var['compare_at_price']
                meta['weight'] = var['weight']
                yield {
                    'cate1Name': meta['cate1Name'],
                    'cate2Name': meta['cate2Name'],
                    'saleUrl': meta['saleUrl'],
                    'dealId': meta['dealId'],
                    'dealName': meta['dealName'],
                    'storingCondition': meta['storingCondition'],
                    'saleStartedAt': meta['saleStartedAt'],
                    'saleEndedAt': meta['saleEndedAt'],
                    'salePrice': meta['salePrice'],
                    'marketPrice': meta['marketPrice'],
                    'mainImgUrl': meta['mainImgUrl'],
                    'unitsold': meta['unitsold'],
                    'optionId': meta['optionId'],
                    'optionName': meta['optionName'],
                    'skuId': meta['skuId'],
                    'option1': meta['option1'],
                    'option2': meta['option2'],
                    'option3': meta['option3'],
                    'isSoldout': meta['isSoldout'],
                    'weight': meta['weight']
                }
        else:
            yield {
                'cate1Name': meta['cate1Name'],
                'cate2Name': meta['cate2Name'],
                'saleUrl': meta['saleUrl'],
                'dealId': meta['dealId'],
                'dealName': meta['dealName'],
                'storingCondition': meta['storingCondition'],
                'saleStartedAt': meta['saleStartedAt'],
                'saleEndedAt': meta['saleEndedAt'],
                'salePrice': meta['salePrice'],
                'marketPrice': None,
                'mainImgUrl': meta['mainImgUrl'],
                'unitsold': meta['unitsold'],
                'optionId': None,
                'optionName': None,
                'skuId': None,
                'option1': None,
                'option2': None,
                'option3': None,
                'isSoldout': meta['isSoldout'],
                'weight': None
            }
