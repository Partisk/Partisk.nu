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
party = Party.objects.get(name='sverigedemokraterna')


class SverigedemokraternaSpider(scrapy.Spider):
    name = "sverigedemokraterna"

    def start_requests(self):
        print('\n# Starting sverigedemokraterna')
        yield scrapy.Request(url='https://sd.se/var-politik/', callback=self.parse_politik)
        yield scrapy.Request(url='https://sd.se/var-politik/var-politik-a-till-o/', callback=self.parse_ao)

    def parse_politik(self, response):
        print('# Importing %s' % response.url)
        elements = response.xpath('//div[contains(@class, "g1-tab-content")]')

        for element in elements:
            yield self.handle_element(response.url, element)

    def parse_ao(self, response):
        print('# Importing %s' % response.url)
        elements = response.xpath('//*[contains(@class, "entry-content")]//*[contains(@class, "g1-grid")]//*[contains(@class, "g1-column")]')

        for element in elements:
            yield self.handle_element(response.url, element)

    def handle_element(self, url, element):
        title_element = element.xpath('self::*/h2/text()')

        if not title_element:
            title = "sverigedemokraterna: Bostadspolitik"
        else:
            title = party.name + ": " + title_element.extract_first()

        print('## Handle %s' % title)
        content = element.xpath('self::*/p/text()').extract_first()

        content = content.encode('utf-8')

        content_hash = hashlib.md5(content).hexdigest()

        if title and content:
            stuff, created = Stuff.objects.get_or_create(
                source_type=website_source_type,
                content_hash=content_hash,
                title=title,
                url=url,
                defaults={
                    'date': date.today(),
                    'content': content,
                }
            )

            if created:
                stuff.parties.add(party)
                print('### Creating entry with hash %s' % content_hash)
