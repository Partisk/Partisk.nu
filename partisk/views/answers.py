from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect

from partisk.models import Question, Answer, Party, from_slug, AnswerType
from partisk.utils import get_questions_params, get_answers_params, get_user
from partisk.forms import AnswerSaveModelForm, AnswerModelForm

VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME


@permission_required('partisk.add_answer')
@csrf_protect
def add_question_answer(request, question_id):
    print('lalal')
    print(question_id)
    question = get_object_or_404(Question, id=question_id)
    party = get_object_or_404(Party, id=request.POST['party'])
    answer_type = get_object_or_404(AnswerType, id=request.POST['answer_type'])
    answer_form = AnswerSaveModelForm(request.POST)

    if answer_form.is_valid():
        answer_form.save()

        messages.success(request, '%ss answer "%s" added for %s' %
                                (party.name,
                                answer_type.answer,
                                question.title))
    else:
        messages.error(request, 'Validation error: %s' %
                                (answer_form.errors))

    return redirect('question', question_title=question.slug)


@permission_required('partisk.add_answer')
@csrf_protect
def add_answer(request):
    print(request.POST)
    print(request.POST['question'])
    print('lols')
    add_question_answer(request, int(request.POST['question']))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@permission_required('partisk.edit_answer')
@csrf_protect
def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    party = get_object_or_404(Party, id=answer.party_id)
    question = get_object_or_404(Question, id=answer.question_id)

    answer_form = AnswerModelForm(request.POST, instance=answer)
    answer = answer_form.save()

    messages.success(request, 'Answer "%s" updated')

    return redirect('answer', question_title=question.slug,
                    party_name=party.name)


@permission_required('partisk.delete_answer')
@csrf_protect
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = get_object_or_404(Question, id=answer.question_id)

    answer.deleted = True
    answer.save()

    messages.success(request, 'Answer deleted')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@cache_page(VIEW_CACHE_TIME)
def answer(request, question_title, party_name):
    question_params = get_questions_params({
        'title': from_slug(question_title)
    })
    question_data = get_object_or_404(Question, **question_params)
    party_data = get_object_or_404(Party, name=from_slug(party_name))

    answer_params = get_answers_params({
        'question_id': question_data.id,
        'party_id': party_data.id
    })
    answer_data = get_object_or_404(Answer, **answer_params)

    answer_text = answer_data.party.name.capitalize()

    if answer_data.answer_type.id == "1":
        answer_text += " tycker att "
    elif answer_data.answer_type.id == "2":
        answer_text += " tycker inte att "
    else:
        answer_text += " har ingen åsikt om " + answer_data.answer_type.id

    answer_text += question_data.title

    form = AnswerModelForm(instance=answer_data) if settings.ADMIN_ENABLED else None

    context = {
        'answer': answer_data,
        'party': party_data,
        'question': question_data,
        'description': answer_text,
        'form': form,
        'user': get_user(request),
        'title': answer_data.party.name.capitalize() + 's svar på om ' +
                                                       question_data.title
    }
    return render(request, 'answer.html', context)
