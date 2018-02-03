import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

class Spider(CrawlSpider):
    name = "ivy"

    allowed_domains = ["musicstore.de"]

    start_urls = [
        "https://www.musicstore.de/en_GR/EUR",
    ]

    rules = [
            Rule(
                LinkExtractor(
                    allow='/en_GR/EUR/',
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
        # The list of items that are found on the particular page
        items = []
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        # Now go through all the found links
        for link in links:
            # Check whether the domain of the URL of the link is allowed; so whether it is in one of the allowed domains
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True
            # If it is allowed, create a new item and add it to the list of found items
            if is_allowed:
                path = '/PATH/TO/sites/musicstore/'
                filename = path + response.url.split("/")[-1] + '.html'
                with open(filename, 'wb') as f:
                    f.write(response.url + "\n")
                    f.write(response.body)

                item = [response.url, link.url]
                items.append(item)
                print(item)
        # Return all the found items
        return items
