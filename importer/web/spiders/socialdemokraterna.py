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
party = Party.objects.get(name='socialdemokraterna')


class SocialdemokraternaSpider(scrapy.Spider):
    name = "socialdemokraterna"

    def start_requests(self):
        print('\n# Starting socialdemokraterna')
        urls = [
            'https://www.socialdemokraterna.se/var-politik/',
            'https://www.socialdemokraterna.se/var-politik/?filter=ghijkl',
            'https://www.socialdemokraterna.se/var-politik/?filter=mnopqr',
            'https://www.socialdemokraterna.se/var-politik/?filter=stuvwx',
            'https://www.socialdemokraterna.se/var-politik/?filter=yz%u00e5%u00e4%u00f6'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        # yield scrapy.Request(url='https://www.socialdemokraterna.se/var-politik/sakomraden/skola/', callback=self.parse_article)

    def parse(self, response):
        urls = response.xpath('//*[contains(@class, "index-catalog__gallery-caption")]//a/@href').extract()

        for url in urls:
            abs_url = urllib.parse.urljoin(response.url, url)
            yield response.follow(abs_url, self.parse_article)

    def parse_article(self, response):
        title = party.name + ": " + response.xpath('//h1/text()').extract_first()
        content = ""
        url = response.url

        print('## Parsing %s' % title)

        content += ''.join(response.xpath('//*[contains(@class, "section__preamble")]').extract())
        content += ''.join(response.xpath('//*[contains(@class, "article")]').extract())
        content += ''.join(response.xpath('//*[contains(@class, "page--key-area__goals")]').extract())

        # Remove random ids
        content = re.sub(r'id=".*"', 'id=""', content)
        content = re.sub(r'onclick=".*"', 'onclick=""', content)
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
