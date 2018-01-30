import scrapy
import os
import sys
import hashlib
import re

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
party = Party.objects.get(name='feministiskt initiativ')


class FeministisktinitiativSpider(scrapy.Spider):
    name = "feministisktinitiativ"

    def start_requests(self):
        print('\n# Starting feministiskt initiativ')
        urls = [
            'https://feministisktinitiativ.se/politik/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//*[contains(@class,"Stack-item")]/@href').extract()

        for url in urls:
            yield response.follow(url, self.parse_article)

    def parse_article(self, response):
        title = party.name + ": " + response.xpath('//h1/text()').extract_first().lstrip()
        content = ""
        url = response.url

        print('## Parsing %s' % title)

        content = ''.join(response.xpath('//div[contains(@class, "Primary")]').extract())
        content = re.sub(r'>\n', '>', content)
        content = re.sub(r'>\\n', '>', content)
        content = re.sub(r'> <', '><', content).encode('utf-8')

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

        boxes = response.xpath('//section[contains(@class,"Accordion-item")]')

        for box in boxes:
            yield self.parse_box(box, title, url)

    def parse_box(self, response, title, url):
        title = party.name + ": " + response.xpath('self::*//h3/text()').extract_first().lstrip()
        content = ""

        print('## Handling %s' % title)

        content = ''.join(response.xpath('self::*//main').extract())
        content = re.sub(r'>\n', '>', content)
        content = re.sub(r'>\\n', '>', content)
        content = re.sub(r'> <', '><', content).encode('utf-8')

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
