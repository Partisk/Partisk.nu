import os
import sys
from datetime import date, timedelta
from twitterscraper import query_tweets

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.external")
sys.path.append('/home/spenen/projects/partisk')

DRY_RUN = False
START_DATE = date(2014, 9, 14)

if __name__ == '__main__':
    print ("Starting Import")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.dev')

    import django
    from django.conf import settings

    django.setup()

    from partisk.models import Tag, Question, Party, Stuff, SourceType, Source


    twitter = SourceType.objects.get(name='twitter')
    sources = Source.objects.filter(source_type=twitter)

    for source in sources:
        print ("# Importing %s" % source.name)

        if not DRY_RUN:
            if source.last_updated and source.last_updated >= date.today():
                print ("## Not updating since %s >= %s" % (source.last_updated, date.today()))
                continue

        args = source.name.split(':')
        name_key = args[0]
        name_value = args[1]

        if DRY_RUN:
            begin_date = START_DATE
        elif source.last_updated:
            begin_date = source.last_updated - timedelta(days=1)
        else:
            begin_date = date.today() - timedelta(days=1)

        print("## Importing from %s" % begin_date)

        if name_key == "party":
            party = Party.objects.filter(id=name_value).first()
            list_of_tweets = query_tweets("from:%s" % source.content, limit=10, begindate=begin_date)

            for tweet in list_of_tweets:
                url = "https://twitter.com/%s/status/%s" % (source.content, tweet.id)
                stuff, created = Stuff.objects.get_or_create(
                    source_type=twitter,
                    date=tweet.timestamp,
                    content=tweet.text,
                    url=url
                )

                if created:
                    stuff.parties.add(party)
                    print("## Tweet %s" % tweet.text)

        source.last_updated = date.today()
        source.save()
