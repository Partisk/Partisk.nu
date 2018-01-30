import json
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, get_object_or_404, redirect
from partisk.models import Party, Answer, from_slug

from partisk.utils import get_questions_for_answers, get_questions_json, \
                          get_answers_json, get_parties_json, \
                          get_qpa_table_data, get_user, get_answers_params, \
                          get_parties_params
from partisk.forms import PartyModelForm


VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME


@permission_required('partisk.add_party')
@csrf_protect
def add_party(request):
    party_form = PartyModelForm(request.POST)
    party_form.save()

    messages.success(request, 'Party "%s" added' % request.POST['name'])

    return redirect(reverse('parties'))


@permission_required('partisk.edit_party')
@csrf_protect
def edit_party(request, party_id):
    party = get_object_or_404(Party, id=party_id)

    party_form = PartyModelForm(request.POST, instance=party)
    party = party_form.save()

    messages.success(request, 'Party "%s" updated' % request.POST['name'])

    return redirect('party', party_name=party.slug)


@permission_required('partisk.delete_party')
@csrf_protect
def delete_party(request, party_id):
    party = get_object_or_404(Party, id=party_id)

    party.deleted = True
    party.save()

    messages.success(request, 'Party %s deleted' % party.name)

    return redirect('party', party_name=party.slug)


@cache_page(VIEW_CACHE_TIME)
def parties(request):
    party_params = get_parties_params()
    parties_data = Party.objects.filter(**party_params) \
                        .order_by('-last_result_parliment')

    parties_representants = []
    parties_other = []

    for party in parties_data:
        if party.last_result_parliment >= 4 or party.last_result_eu >= 4:
            parties_representants.append(party)
        else:
            parties_other.append(party)

    parties_1 = parties_representants[:len(parties_representants)//2 + 1]
    parties_2 = parties_representants[len(parties_representants)//2 + 1:]

    form = PartyModelForm() if settings.ADMIN_ENABLED else None

    context = {
        'official':
            {'left': parties_1,
             'right': parties_2},
        'other':
            {'left': parties_other},
        'user': get_user(request),
        'form': form
    }

    return render(request, 'parties.html', context)


@permission_required('partisk.delete_party')
@csrf_protect
def delete_party(request, party_id):
    party = get_object_or_404(Party, id=party_id)

    party.deleted = True
    party.save()

    messages.success(request, 'Party "%s" deleted' % party.name)

    return redirect('parties')


@cache_page(VIEW_CACHE_TIME)
def party(request, party_name):
    party_params = get_parties_params({
        'name': from_slug(party_name)
    })
    party_data = get_object_or_404(Party, **party_params)
    answer_params = get_answers_params({
        'party_id': party_data.id,
        'answer_type_id__isnull': False
    })
    answers_data = Answer.objects.filter(**answer_params)
    questions_data = get_questions_for_answers(answers_data)

    data = {
        'questions': get_questions_json(questions_data),
        'answers': get_answers_json(answers_data),
        'parties': get_parties_json([party_data])
    }

    json_data = json.dumps(data, separators=(',', ':'))

    form = PartyModelForm(instance=party_data) if settings.ADMIN_ENABLED else None

    context = {
        'party': party_data,
        'qpa': get_qpa_table_data(questions_data, answers_data, [party_data]),
        'data': json_data,
        'form': form,
        'user': get_user(request),
    }

    return render(request, 'party.html', context)

