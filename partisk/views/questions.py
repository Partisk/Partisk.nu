import json
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from partisk.models import Question, Tag, Party, Answer, QuestionTags, \
                    from_slug
from partisk.utils import get_questions_json, get_answers_json, \
                    get_parties_json, get_user, get_tags_for_question, \
                    get_qpa_table_data, get_questions_params, \
                    get_answers_params, get_parties_params
from partisk.forms import QuestionModelForm, AnswerModelForm

VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME


def add_tags(request, question, clean=False):
    data = request.POST
    if data.get('tags', None):
        if clean:
            QuestionTags.objects.filter(question_id=question.id).delete()

        tags = [t.strip() for t in data['tags'].split(',')]

    for name in tags:
        tag, created = Tag.objects.get_or_create(
            name=name,
            defaults={
                'created_by': request.user.id,
                'updated_by': None,
                'deleted': False,
                'is_category': False
            }
        )

        QuestionTags.objects.create(tag=tag, question=question)

        if created:
            messages.success(request, 'Tag "%s" added' % tag)


@login_required
@permission_required('partisk.add_question')
@csrf_protect
def add_question(request):
    question_form = QuestionModelForm(request.POST)
    question = question_form.save()

    add_tags(request, question)

    messages.success(request, 'Question "%s" added' % request.POST['title'])

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@permission_required('partisk.edit_question')
@csrf_protect
def edit_question(request, question_id):
    question_params = get_questions_params({
        'id': question_id
    })
    question = get_object_or_404(Question, **question_params)

    question_form = QuestionModelForm(request.POST, instance=question)
    question = question_form.save()

    add_tags(request, question, True)

    messages.success(request, 'Question "%s" updated' % request.POST['title'])

    return redirect('question', question_title=question.slug)


@login_required
@permission_required('partisk.delete_question')
@csrf_protect
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    question.deleted = True
    question.save()

    messages.success(request, 'Question "%s" deleted' % question.title)

    return redirect('questions')


@cache_page(VIEW_CACHE_TIME)
def questions(request):
    question_params = get_questions_params()
    questions_data = Question.objects.filter(**question_params)
    answer_params = get_answers_params({
        'answer_type_id__isnull': False
    })
    answers_data = Answer.objects.filter(**answer_params)
    party_params = get_parties_params()
    parties_data = Party.objects.filter(**party_params) \
                        .order_by('-last_result_parliment')

    data = {
        'questions': get_questions_json(questions_data),
        'answers': get_answers_json(answers_data),
        'parties': get_parties_json(parties_data),
    }

    json_data = json.dumps(data, separators=(',', ':'))

    form = QuestionModelForm() if settings.ADMIN_ENABLED else None

    context = {'data': json_data, 'user': get_user(request), 'form': form}

    return render(request, 'questions.html', context)


@cache_page(VIEW_CACHE_TIME)
def question(request, question_title):
    question_params = get_questions_params({
        'title': from_slug(question_title)
    })
    question_data = get_object_or_404(Question, **question_params)
    answer_params = get_answers_params({
        'question_id': question_data.id,
        'answer_type_id__isnull': False
    })
    answers_data = Answer.objects.filter(**answer_params)
    party_params = get_parties_params()
    parties_data = Party.objects.filter(**party_params) \
                        .order_by('-last_result_parliment')
    tags_data = get_tags_for_question(question_data.id)

    data = {
        'questions': get_questions_json([question_data]),
        'answers': get_answers_json(answers_data),
        'parties': get_parties_json(parties_data)
    }

    tags_string = ', '.join([tag.name for tag in tags_data])

    json_data = json.dumps(data, separators=(',', ':'))

    if settings.ADMIN_ENABLED:
        question_form = QuestionModelForm(instance=question_data)
        answer_form = AnswerModelForm()
    else:
        question_form = None
        answer_form = None

    context = {
        'question': question_data,
        'qpa': get_qpa_table_data([question_data], answers_data, parties_data),
        'tags': tags_data,
        'data': json_data,
        'question_form': question_form,
        'answer_form': answer_form,
        'user': get_user(request),
        'tags_string': tags_string
    }
    return render(request, 'question.html', context)
