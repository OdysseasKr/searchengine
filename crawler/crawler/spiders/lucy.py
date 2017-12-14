import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

class Spider(CrawlSpider):
    name = "lucy"

    allowed_domains = ["e-shop.gr"]

    start_urls = [
        "http://www.e-shop.gr/",
    ]

    rules = [
            Rule(
                LinkExtractor(
                    canonicalize=True,
                    unique=True
                ),
                follow=True,
                callback="parse_items"
            )
        ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)


    def parse_items(self, response):
        items = []

        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        for link in links:
            is_allowed = False

            for allowed_domain in self.allowed_domains:
                if (allowed_domain in link.url):
                    is_allowed = True

            if (is_allowed):
                path = '/PATH/TO/STORE/PAGES'
                filename = path + response.url.split("/")[-1] + '.html'
                
                with open(filename, 'wb') as f:
                    f.write(response.body)

                item = [response.url, link.url]
                items.append(item)
                print(item)

        return items
