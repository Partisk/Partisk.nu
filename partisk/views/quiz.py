import subprocess
import uuid
import json
import datetime
import os
from geolite2 import geolite2
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.urls import reverse
from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, get_object_or_404, redirect
from partisk.models import Quiz, Party, Answer, \
                    from_slug, QuizAnswer, QuizResultsInfo, \
                    QuizResults, Kommun, Lan
from partisk.utils import get_qpa_table_data, get_user, \
                          get_questions_for_answers, \
                          get_answers_for_questions, \
                          get_qpa_table_data_with_quiz_results, \
                          get_questions_for_quiz, get_answers_params, \
                          get_quizzes_params, get_parties_params, get_lans_json, \
                          get_kommuner_json
from partisk.forms import QuizModelForm

VIEW_CACHE_TIME = settings.VIEW_CACHE_TIME

geo_reader = geolite2.reader()


@permission_required('partisk.add_quiz')
@csrf_protect
def add_quiz(request):
    quiz_form = QuizModelForm(request.POST)
    quiz_form.save()

    messages.success(request, 'Quiz "%s" added' % request.POST['name'])

    return redirect(reverse('quizzes'))


@permission_required('partisk.edit_quiz')
@csrf_protect
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    quiz_form = QuizModelForm(request.POST, instance=quiz)
    quiz = quiz_form.save()

    messages.success(request, 'Quiz "%s" updated' % request.POST['name'])

    return redirect('quiz', quiz_name=quiz.slug)


@permission_required('partisk.delete_quiz')
@csrf_protect
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    quiz.deleted = True
    quiz.save()

    messages.success(request, 'Quiz "%s" deleted' % quiz.name)

    return redirect('quizzes')


def graph_image(request, quiz_result_id):
    abspath = settings.GENERATED_IMG_PATH + quiz_result_id + '.jpg'

    quiz_results = QuizResults.objects.get(id=quiz_result_id)

    

    # mainParties = [x for x in parties  if x.last_result_parliment > 4]
    # otherParties = [x for x in parties  if x.last_result_parliment < 4]

    generate_quiz_result_image(quiz_results, quiz_result_id)

    # kolla sa att det bara innehaller siffror och bokstaver
    fsock = open(abspath, "rb")

    response = HttpResponse(fsock, content_type='image/jpg')
    response['Content-Length'] = os.stat(abspath).st_size

    return response


def generate_quiz_result_image(results, id):
    party_params = get_parties_params()
    
    parties = Party.objects.filter(**party_params)
    no_parties = len(parties)
    

    padd_x = 25
    padd_y = 100
    height = 600
    width = 600
    logo_padding_top = 10
    logo_dim = padd_x
    bar_between = 25
    bar_width = (width - bar_between * (no_parties - 1) - padd_x * 2) \
        / no_parties
    bar_max_height = height - 2 * padd_y - logo_dim - logo_padding_top
    text_padding_bottom = 5
    text_character_width = 4
    font_size = 12

    blocks = ""
    texts = ""

    r = json.loads(results.data)

    for i, p in enumerate(parties):
        result = r[str(p.id)]
        total = result['correct'] + result['incorrect']

        if total != 0:
            score = result['correct']/total
        else:
            score = 0

        left = padd_x + i * (bar_width + bar_between)
        scoreStr = str(round(score * 100.0)) + "%"
        text_padding = (3 - len(scoreStr) + 1) * text_character_width
        top = padd_y + bar_max_height - bar_max_height * score

        block_args = {
            'score': scoreStr,
            'top': top,
            'left': left,
            'bottom': height - padd_y - logo_dim - logo_padding_top,
            'logo_bottom': height - padd_y - logo_dim,
            'right': left + bar_width,
            'party_id': p.id,
            'img_dim': bar_width,
            'text_left': left + text_padding,
            'text_top': top - text_padding_bottom,
            'color': p.color
        }

        blocks = blocks + ''' -fill "{color}" -draw '''.format(**block_args)

        if score > 0.0:
            blocks = blocks + '''"rectangle {left},{top} {right},{bottom} ''' \
                              .format(**block_args)
        else:
            blocks = blocks + '''"'''

        print(score)

        blocks = blocks + '''image over {left},{logo_bottom} {img_dim},{img_dim} 'generate/images/large/{party_id}.png'"'''.format(**block_args)
        texts = texts + ''' -fill "{color}" -draw "translate -0,-0 text {text_left},{text_top} '{score}'" '''.format(**block_args)

    command_args = {
        'width': width,
        'height': height,
        'blocks': blocks,
        'id': id,
        'texts': texts,
        'font_size': font_size,
        'crop_width': width - 10,
        'crop_height': height - 10,
        'outfile': settings.GENERATED_IMG_PATH + id + '.jpg'
    }

    command = '''convert -font Ubuntu -pointsize {font_size} -fill black -size {width}x{height} xc:transparent \
         -crop {crop_width}x{crop_height}+0+0 +repage {blocks} \( +clone -background "#666" -shadow 30x3+4+3 \) \
         \( -repage +20+20 generate/images/logo.png \) \
         \( {texts} \) \
         \( generate/images/bg.jpg \) \
        -reverse -layers merge -crop {width}x{height} -flatten {outfile}''' \
             .format(**command_args)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()


def calculate_quiz_results(questions, a_data, city):
    party_params = get_parties_params()


    parties = Party.objects.filter(**party_params) \
                   .order_by('-last_result_parliment')

    question_ids = [q.id for q in questions]
    answer_params = get_answers_params({
        'question_id__in': question_ids,
        'answer_type_id__isnull': False
    })
    answers = Answer.objects.filter(**answer_params)

    qa = get_qpa_table_data(questions, answers, parties)

    parties_map = {}

    for p in parties:
        parties_map[p.id] = {
            'answers': 0,
            'correct': 0,
            'incorrect': 0,
            'points': 0
        }

    for _, qd in qa['questions'].items():
        q = qd['question']
        for ad in qd['answers']:
            ua = a_data.get(str(q.id))
            if ua and ad and ad.get('answer'):
                a = ad['answer']
                party_entry = parties_map[a.party_id]
                if a.answer_type_id == ua:
                    party_entry['correct'] += 1
                elif ua != "0":
                    party_entry['incorrect'] += 1

                if a.answer_type_id is not None:
                    party_entry['answers'] += 1

    return parties_map


@cache_page(VIEW_CACHE_TIME)
def quiz_results(request, quiz_result_id):
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

    main_parties = [x for x in parties  if x.last_result_parliment > 4]
    other_parties = [x for x in parties  if x.last_result_parliment < 4]

    for party in parties:
        parties_json[party.id] = {
            'name': party.name,
            'color': party.color,
            'main':bool(party.last_result_parliment > 4)
        }

    return render(request, "results.html", {
        'result': json.loads(result.data),
        'data': result.data,
        'parties_json': json.dumps(parties_json),
        'parties': parties,
        'main_parties':main_parties,
        'other_parties':other_parties,
        'quiz': quiz,
        'quiz_result_id': quiz_result_id,
        'created': created,
        'description': 'Resultat för ' + quiz.name,
        'title': 'Resultat för ' + quiz.name,
        'image': request.build_absolute_uri() + 'img.jpg',
        'qa': qa})


def save_quiz_results(request):
    if request.method == "POST":
        quiz_id = int(request.POST["quiz_id"])
        quiz_data = get_object_or_404(Quiz, id=quiz_id)

        kommun = request.POST.get("kommun")
        lan = request.POST.get("lan")

        user_kommun_id = int(kommun) if kommun else None
        user_lan_id = lan

        ip = request.META.get('HTTP_X_FORWARDED_FOR')

        reader = None
        if ip:
            reader = geo_reader.get(ip)

        country = ''
        city = ''
        postal = ''
        coordinates = ''
        accuracy = -1
        subdivision = []

        if reader:
            country = reader.get('country', {}).get('names', {}).get('en', '')
            city = reader.get('city', {}).get('names', {}).get('en', '')
            postal = reader.get('postal', {}).get('code', '')
            lat = reader.get('location', {}).get('latitude', 0)
            lng = reader.get('location', {}).get('longitude', 0)

            if lat and lng:
                coordinates = str(lat) + ':' + str(lng)

            accuracy = reader.get('location', {}).get('accuracy_radius', -1)

            for s in reader.get('subdivisions', []):
                subdivision.append(s['names']['en'])

        questions_data = get_questions_for_quiz(quiz_data.id)

        answers_data = {}

        result_id = uuid.uuid4().hex
        result_info_id = uuid.uuid4().hex

        quiz_results_data = calculate_quiz_results(questions_data,
                                                   request.POST, city)

        quiz_results = QuizResults(id=result_id,
                                   data=json.dumps(quiz_results_data),
                                   version=0, quiz_id=quiz_id)
        quiz_results.save()

        quiz_results_info = QuizResultsInfo(id=result_info_id,
                                            quiz_id=quiz_id,
                                            country=country,
                                            city=city,
                                            postal_code=postal,
                                            accuracy=accuracy,
                                            date=datetime.date.today(),
                                            coordinates=coordinates,
                                            lan_id=user_lan_id,
                                            kommun_id=user_kommun_id,
                                            subdivision=''.join(subdivision))
        quiz_results_info.save()

        # Make all queries in same sql transaction
        with transaction.atomic():
            # todo, commit this
            for q in questions_data:
                qaid = uuid.uuid4().hex
                qid = q.id
                a = int(request.POST.get(str(qid)))
                answers_data[qid] = a
                qa = QuizAnswer(id=qaid, question_id=int(qid),
                                answer_type_id=a, importance=0,
                                quiz_results_info_id=result_info_id)
                qa.save()

        request.session['quiz_results_id'] = result_info_id

        return redirect(reverse('quiz_results',
                                kwargs={'quiz_result_id': result_id}))


@cache_page(VIEW_CACHE_TIME)
def quizzes(request):
    quiz_params = get_quizzes_params()
    quizzes_data = Quiz.objects.filter(**quiz_params)
    form = QuizModelForm() if settings.ADMIN_ENABLED else None
    context = {'quizzes': quizzes_data, 'form': form,
               'user': get_user(request)}
    return render(request, 'quizzes.html', context)


@cache_page(VIEW_CACHE_TIME)
@csrf_protect
def quiz(request, quiz_name):
    quiz_params = get_quizzes_params({
        'name': from_slug(quiz_name)
    })
    quiz_data = get_object_or_404(Quiz, **quiz_params)
    questions_data = get_questions_for_quiz(quiz_data.id)
    kommuner_data = get_kommuner_json(Kommun.objects.all())
    lan_data = get_lans_json(Lan.objects.all())
    form = QuizModelForm(instance=quiz_data) if settings.ADMIN_ENABLED else None
    context = {'quiz': quiz_data, 'questions': questions_data,
               'kommuner': json.dumps(kommuner_data, separators=(',', ':')),
               'lan': json.dumps(lan_data, separators=(',', ':')),
               'form': form, 'user': get_user(request)}
    return render(request, 'quiz.html', context)
