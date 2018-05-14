import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.template.defaulttags import register
from partisk.models import Question, Tag, Quiz, Party, QuizAnswer, QuizResults
from partisk.utils import get_questions_params, get_quizzes_params, \
                          get_parties_params, get_tags_params
from django.shortcuts import get_object_or_404

from partisk.utils import get_qpa_table_data, get_user, \
                          get_questions_for_answers, \
                          get_answers_for_questions, \
                          get_qpa_table_data_with_quiz_results, \
                          get_questions_for_quiz, get_answers_params, \
                          get_quizzes_params, get_parties_params, get_lans_json, \
                          get_kommuner_json

VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def error404(request):
    return render(request, 'error.html', status=404)


def error500(request):
    return render(request, 'error.html', status=500)


def error403(request):
    return render(request, 'error.html', status=403)


def error400(request):
    return render(request, 'error.html', status=400)


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


def test(request):
    quiz_result_id = "ba169d29b3504d47b4cbdeb69ff41a5b"
    result = get_object_or_404(QuizResults, id=quiz_result_id)
    quiz = get_object_or_404(Quiz, id=result.quiz_id)
    party_params = get_parties_params()
    parties = Party.objects.filter(**party_params)
    created = result.created
    qa = {}

    if request.session.get('quiz_results_id', False):
        quiz_results_id = request.session['quiz_results_id']
        party_params = get_parties_params()
        parties_data = Party.objects.filter(**party_params) \
                            .order_by('-last_result_parliment')
        quiz_answers_data = QuizAnswer.objects.filter(
            quiz_results_info__id=quiz_results_id)
        questions_data = get_questions_for_answers(quiz_answers_data)
        answers_data = get_answers_for_questions(questions_data)
        qa = get_qpa_table_data_with_quiz_results(questions_data, answers_data,
                                                  parties_data,
                                                  quiz_answers_data)

    parties_json = {}
    for party in parties:
        parties_json[party.id] = {
            'name': party.name,
            'color': party.color
        }

    return render(request, "test.html", {
        'result': json.loads(result.data),
        'data': result.data,
        'parties_json': json.dumps(parties_json),
        'parties': parties,
        'quiz': quiz,
        'quiz_result_id': quiz_result_id,
        'created': created,
        'description': 'Resultat för ' + quiz.name,
        'title': 'Resultat för ' + quiz.name,
        'image': request.build_absolute_uri() + 'img.jpg',
        'qa': qa})


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
