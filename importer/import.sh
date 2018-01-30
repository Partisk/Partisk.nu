#!/bin/bash

scrapy crawl --nolog socialdemokraterna
scrapy crawl --nolog moderaterna
scrapy crawl --nolog sverigedemokraterna
scrapy crawl --nolog centerpartiet
scrapy crawl --nolog vansterpartiet
scrapy crawl --nolog liberalerna
scrapy crawl --nolog miljopartiet
scrapy crawl --nolog kristdemokraterna
scrapy crawl --nolog feministisktinitiativ

python -m twitter
