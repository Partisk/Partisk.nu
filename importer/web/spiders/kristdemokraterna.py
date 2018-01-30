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
party = Party.objects.get(name='kristdemokraterna')


class KristdemokraternaSpider(scrapy.Spider):
    name = "kristdemokraterna"

    def start_requests(self):
        print('\n# Starting kristdemokraterna')
        #yield scrapy.Request(url='https://kristdemokraterna.se/var-politik/politikomraden/', callback=self.parse_politik)
        yield scrapy.Request(url='https://kristdemokraterna.se/politik-a-o/', callback=self.parse_ao)

    def parse_politik(self, response):
        urls = response.xpath('//*[contains(@class, "link-list")]//a/@href').extract()

        for url in urls:
            yield response.follow(url, self.parse_article)

    def parse_ao(self, response):
        print('# Importing %s' % response.url)
        elements = response.xpath('//main//ul[contains(@class, "o-bare-list o-bare-list--spaced")]/li')

        for element in elements:
            yield self.handle_element(response.url, element)

    def handle_element(self, url, element):
        title = party.name + ": " + element.xpath('self::*//strong/text()').extract_first().lstrip()

        print('## Handle %s' % title)
        content = element.xpath('self::*').extract_first()

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

    def parse_article(self, response):
        title = party.name + ": " + response.xpath('//main//h1/text()').extract_first().lstrip()
        content = ""
        url = response.url

        print('## Parsing %s' % title)

        content = ''.join(response.xpath('//article').extract())

        content = content.encode('utf-8')

        content_hash = hashlib.md5(content).hexdigest()

        stuff, created = Stuff.objects.get_or_create(
            source_type=website_source_type,
            url=url,
            content_hash=content_hash,
            title=title,
            defaults={
                'date': date.today(),
                'content': content,
            }
        )

        if created:
            stuff.parties.add(party)
            print('### Creating entry with hash %s' % content_hash)
