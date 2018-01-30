import scrapy
import os
import sys
import hashlib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.external")
sys.path.append('/home/spenen/projects/partisk')

import django
from django.conf import settings

django.setup()

from partisk.models import Party, SourceType, Stuff
import urllib
from scrapy_djangoitem import DjangoItem
from datetime import date

website_source_type = SourceType.objects.get(name='website')
party = Party.objects.get(name='vänsterpartiet')


class VansterpartietSpider(scrapy.Spider):
    name = "vansterpartiet"

    def start_requests(self):
        print("\n# Starting vansterpartiet")
        urls = [
            'http://www.vansterpartiet.se/politik',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//*[@id="politik"]/option/@value').extract()

        for url in urls:
            yield response.follow(url, self.parse_article)

    def parse_article(self, response):
        title = party.name + ": " + response.xpath('//h1/text()').extract_first()
        url = response.url

        print('## Parsing %s' % title)

        content = ''.join(response.xpath('//div[contains(@class, "entry-content")]').extract()).encode('utf-8')

        content_hash = hashlib.md5(content).hexdigest()

        stuff, created = Stuff.objects.get_or_create(
            source_type=website_source_type,
            content_hash=content_hash,
            url=url,
            title=title,
            defaults={
                'date': date.today(),
                'content': content,
            }
        )

        if created:
            stuff.parties.add(party)
            print('### Creating entry with hash %s' % content_hash)
