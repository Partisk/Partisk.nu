# https://realpython.com/testing-in-django-part-1-best-practices-and-examples/

from django.test import TestCase
from partisk.models import Question


class TestQuestions(TestCase):
    fixtures = ['partisk.yaml', ]

    def test_get_question(self):
            q = Question.objects.get(pk=1)
            self.assertEquals(q.title, 'Question 1')
