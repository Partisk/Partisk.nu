import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.template.defaulttags import register
from partisk.models import Question, Tag, Quiz, Party
from partisk.utils import get_questions_params, get_quizzes_params, \
                          get_parties_params, get_tags_params

VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def get_social_data(title, description, image=None):
    data = {
        'title': title,
        'description': description,
    }

    if image is None:
        data['image'] = settings.STATIC_PATH + '/images/logo.png'
    else:
        data['image'] = image

    return data


def index(request):
    return render(request, 'index.html')


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


@cache_page(VIEW_CACHE_TIME)
def search(request):
    if request.method == 'GET':
        query = request.GET["query"]

        # Min character length for performing a search
        if len(query) > 2:
            party_params = get_parties_params({
                'name__icontains': query
            })
            parties = Party.objects.filter(**party_params).order_by('name')
            question_params = get_questions_params({
                                'title__icontains': query
                              })
            questions = Question.objects.filter(
                **question_params).order_by('title')
            tag_params = get_tags_params({
                'name__icontains': query
            })
            tags = Tag.objects.filter(**tag_params).order_by('name')
            quizzes_params = get_quizzes_params({
                'name__icontains': query
            })
            quizzes = Quiz.objects.filter(**quizzes_params).order_by('name')

            parties_data = [{'data': {'id': p.id, 'cat': 'Parties', 'type': 'p'}, 'value': p.name} for p in parties]
            questions_data = [{'data': {'id': q.id, 'cat': 'Questions', 'type': 'q'}, 'value': q.title} for q in questions]
            tags_data = [{'data': {'id': t.id, 'cat': 'Tags', 'type': 't'}, 'value': t.name} for t in tags]
            quizzes_data = [{'data': {'id': q.id, 'cat': 'Quizzes', 'type': 'z'}, 'value': q.name} for q in quizzes]

            suggestions = parties_data + questions_data + tags_data + quizzes_data

            data = {
                'query': query,
                'suggestions': suggestions
            }

            return HttpResponse(json.dumps(data), content_type='application/json')
