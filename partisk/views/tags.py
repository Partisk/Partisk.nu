import json
from itertools import groupby
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from partisk.models import Question, Tag, Party, QuestionTags, \
                    from_slug
from partisk.utils import get_questions_for_tag, \
                          get_answers_for_questions, get_questions_json, \
                          get_parties_json, get_answers_json, \
                          get_qpa_table_data, get_questions_params, \
                          get_tags_params, get_parties_params, get_user
from partisk.forms import TagModelForm

VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME


@permission_required('partisk.add_tag')
@csrf_protect
def add_tag(request):
    tag_form = TagModelForm(request.POST)
    tag_form.save()

    messages.success(request, 'Tag "%s" added' % request.POST['name'])

    return redirect(reverse('tags'))


@permission_required('partisk.edit_tag')
@csrf_protect
def edit_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    tag_form = TagModelForm(request.POST, instance=tag)
    tag = tag_form.save()

    messages.success(request, 'Tag "%s" updated' % request.POST['name'])

    return redirect('tag', tag_name=tag.slug)


@permission_required('partisk.delete_tag')
@csrf_protect
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    tag.deleted = True
    tag.save()

    messages.success(request, 'Tag "%s" deleted' % tag.name)

    return redirect('tags')


def get_no_questions_for_tags():
    question_tag_ids = QuestionTags.objects \
                                   .values_list("question_id", "tag_id")
    question_ids = [qt[0] for qt in question_tag_ids]
    question_params = get_questions_params({'id__in': question_ids})
    questions_data = Question.objects.filter(**question_params)
    questions_map = {str(q.id): q for q in questions_data}

    no_questions = {}
    for qt in question_tag_ids:
        q = questions_map.get(str(qt[0]))

        if q:
            no_questions.setdefault(qt[1], []).append(q.id)

    return no_questions


@cache_page(VIEW_CACHE_TIME)
def tags(request):
    tag_params = get_tags_params()
    tags_data = Tag.objects.filter(**tag_params).order_by('name')
    no_questions_data = get_no_questions_for_tags()

    tag_items = []
    for tag_item in tags_data:
        no_data = no_questions_data.get(tag_item.id)

        if no_data:
            no_questions = len(no_data)

            tag_items.append({
                'tag': tag_item,
                'no_questions': no_questions
            })

    tag_items.sort(key=lambda t: t['tag'].name)
    divider = tag_items[len(tag_items)//2 + 1]['tag'].name[0]

    category_tags_left = []
    category_tags_right = []

    # Group the tags by first letter
    for letter, items in groupby(tag_items, key=lambda t: t['tag'].name[0]):
        item = {
            'letter': letter,
            'items': list(items)
        }

        if letter <= divider:
            category_tags_left.append(item)
        else:
            category_tags_right.append(item)

    context = {
        'category_tags': [category_tags_left, category_tags_right],
    }

    return render(request, 'tags.html', context)


@cache_page(VIEW_CACHE_TIME)
def tag(request, tag_name):
    tag_data = get_object_or_404(Tag, name=from_slug(tag_name))
    questions_data = get_questions_for_tag(tag_data.id)
    answers_data = get_answers_for_questions(questions_data)
    party_params = get_parties_params()
    parties_data = Party.objects.filter(**party_params) \
                        .order_by('-last_result_parliment')

    data = {
        'questions': get_questions_json(questions_data),
        'answers': get_answers_json(answers_data),
        'parties': get_parties_json(parties_data)
    }

    json_data = json.dumps(data, separators=(',', ':'))

    form = TagModelForm(instance=tag_data) if settings.ADMIN_ENABLED else None

    context = {
        'tag': tag_data,
        'qpa': get_qpa_table_data(questions_data, answers_data, parties_data),
        'form': form,
        'data': json_data,
        'user': get_user(request)
    }

    return render(request, 'tag.html', context)

