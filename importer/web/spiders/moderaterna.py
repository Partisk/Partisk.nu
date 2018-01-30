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
party = Party.objects.get(name='moderaterna')


class ModeraternaSpider(scrapy.Spider):
    name = "moderaterna"

    def start_requests(self):
        urls = [
            'https://moderaterna.se/var-politik',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print('\n# Starting moderaterna')
        urls = response.xpath('//div[contains(@class, "o-our-politics")]//a/@href').extract()

        urls.append('/var-politik-i-korthet')

        for url in urls:
            abs_url = urllib.parse.urljoin(response.url, url)
            yield response.follow(abs_url, self.parse_article)

    def parse_article(self, response):
        title = party.name + ": " + response.xpath('//h1/span/text()').extract_first()
        content = ""
        url = response.url

        print('## Parsing %s' % title)

        content += ''.join(response.xpath('//*[contains(@class, "a-lead")]').extract())
        content += ''.join(response.xpath('//*[contains(@class, "o-article__body")]').extract())

        content = content.encode('utf-8')

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

        additional_urls = response.xpath('//*[contains(@class, "field-page-related")]//a/@href').extract()

        for additional_url in additional_urls:
            abs_url = urllib.parse.urljoin(response.url, additional_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_article)
