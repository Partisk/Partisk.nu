from django.conf import settings
from partisk.models import QuestionTags, Tag, Question, Answer, QuestionQuizzes


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def get_params(params, include_deleted, include_approved):
    args = {'deleted': False}

    if not settings.ADMIN_ENABLED:
        # if include_deleted:
        #    args['deleted'] = False
        if include_approved:
            args['approved'] = True

    return merge_two_dicts(params, args)


def get_questions_params(params={}):
    return get_params(params, True, True)


def get_quizzes_params(params={}):
    return get_params(params, True, True)


def get_answers_params(params={}):
    return get_params(params, True, True)


def get_parties_params(params={}):
    return get_params(params, True, False)


def get_tags_params(params={}):
    return get_params(params, True, False)


def get_parties_json(parties):
    return [{
        'n': party.name,
        'i': int(party.id),
        's': party.slug,
        'x': party_has_reps(party),
    } for party in parties]


def get_questions_json(questions):
    return [{
        't': question.title,
        's': question.slug,
        'i': int(question.id)
    } for question in questions]


def get_lans_json(lans):
    return [{
        'id': lan.id,
        'name': lan.name
    } for lan in lans]


def get_kommuner_json(kommuner):
    return [{
        'id': kommun.id,
        'lan': kommun.lan,
        'name': kommun.name
    } for kommun in kommuner]


def get_answers_json(answers):
    return [{
        'a': int(answer.answer_type_id),
        'q': int(answer.question_id),
        'p': int(answer.party_id)
    } for answer in answers]


def get_tags_for_question(qid):
    tag_ids = QuestionTags.objects.filter(question_id=qid) \
                          .values_list('tag_id', flat=True)
    return Tag.objects.filter(id__in=tag_ids)


def get_questions_for_tag(tid):
    question_ids = QuestionTags.objects.filter(tag_id=tid) \
                               .values_list('question_id', flat=True)
    question_params = get_questions_params({'id__in': question_ids})
    return Question.objects.filter(**question_params)


def get_questions_for_quiz(qid):
    question_ids = QuestionQuizzes.objects.filter(quiz_id=qid) \
                                  .values_list('question_id', flat=True)
    question_params = get_questions_params({'id__in': question_ids})
    return Question.objects.filter(**question_params)


def get_questions_for_answers(answers):
    qids = [a.question_id for a in answers]
    question_params = get_questions_params({'id__in': qids})
    return Question.objects.filter(**question_params)


def get_answers_for_questions(questions):
    qids = [q.id for q in questions]
    answer_params = get_answers_params({
        'question_id__in': qids, 'answer_type_id__isnull': False
    })
    return Answer.objects.filter(**answer_params)


def get_qpa_table_data(questions, answers, parties):
    qpa = {'parties': parties, 'questions': {}}

    party_index_map = {str(p.id): i for i, p in enumerate(parties)}
    questions_map = {str(q.id): q for q in questions}
    parties_map = {str(p.id): p for p in parties}

    print (parties_map)
    print (questions_map)

    for answ in answers:
        qid = str(answ.question_id)
        pid = str(answ.party_id)

        print (qid, pid)
        if qid in questions_map and pid in parties_map:
            if qid not in qpa['questions']:
                qpa['questions'][qid] = {
                    'answers': [{'party': p} for p in parties],
                    'question': questions_map[qid]
                }

            qpa['questions'][qid]['answers'][party_index_map[pid]]['answer'] = answ

    return qpa


def get_qpa_table_data_with_quiz_results(
    questions, answers, parties, quiz_answers
):
    qpa = get_qpa_table_data(questions, answers, parties)

    quiz_answers_map = {str(a.question_id): a for a in quiz_answers}

    for k, q in qpa['questions'].items():
        q['quiz_answer'] = quiz_answers_map[k]

    return qpa


def get_user(request):
    user = request.user

    return {
        'answer': {
            'add': user.has_perm('partisk.add_answer'),
            'edit': user.has_perm('partisk.edit_answer'),
            'delete': user.has_perm('partisk.delete_answer'),
        },
        'quiz': {
            'add': user.has_perm('partisk.add_quiz'),
            'edit': user.has_perm('partisk.edit_quiz'),
            'delete': user.has_perm('partisk.delete_quiz'),
        },
        'question': {
            'add': user.has_perm('partisk.add_question'),
            'edit': user.has_perm('partisk.edit_question'),
            'delete': user.has_perm('partisk.delete_question'),
        },
        'tag': {
            'add': user.has_perm('partisk.add_tag'),
            'edit': user.has_perm('partisk.edit_tag'),
            'delete': user.has_perm('partisk.delete_tag'),
        },
        'party': {
            'add': user.has_perm('partisk.add_party'),
            'edit': user.has_perm('partisk.edit_party'),
            'delete': user.has_perm('partisk.delete_party'),
        }
    }


def party_has_reps(party):
    return party.last_result_parliment >= 4
