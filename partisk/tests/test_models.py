# https://realpython.com/testing-in-django-part-1-best-practices-and-examples/

from django.test import TestCase
from partisk.models import Question, Party, Tag, Quiz


class TestSlugs(TestCase):
    fixtures = ['partisk.yaml', ]

    def test_question_slug(self):
        q = Question.objects.get(pk=1)
        self.assertEquals(q.slug, 'question_1')

    def test_party_slug(self):
        p = Party.objects.get(pk=1)
        self.assertEquals(p.slug, 'party_1')

    def test_quiz_slug(self):
        q = Quiz.objects.get(pk=1)
        self.assertEquals(q.slug, 'quiz_1')

    def test_tag_slug(self):
        t = Tag.objects.get(pk=1)
        self.assertEquals(t.slug, 'tag_1')
