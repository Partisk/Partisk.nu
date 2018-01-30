from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from partisk.views import index
from partisk.views import questions, add_question, delete_question, \
                          edit_question, question
from partisk.views import parties, add_party, delete_party, edit_party, party
from partisk.views import tags, add_tag, delete_tag, edit_tag, tag
from partisk.views import quizzes, add_quiz, delete_quiz, edit_quiz, \
                          save_quiz_results, quiz_results, quiz
from partisk.views import answer, add_answer, delete_answer, edit_answer
from partisk.views import stuff, admin_index, handle
from partisk.views import search
from partisk.views import contact
from partisk.views import about
from partisk.views import graph_image
from partisk.views import login, logout

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^frågor/$', questions, name='questions'),
    url(r'^frågor/(?P<question_title>.+)/(?P<party_name>.+)/$', answer,
        name='question_for_party'),
    url(r'^frågor/(?P<question_title>.+)/$', question, name='question'),
    url(r'^partier/$', parties, name='parties'),
    url(r'^partier/(?P<party_name>.+)/$', party, name='party'),
    url(r'^svar/(?P<question_title>.+)/(?P<party_name>.+)/$', answer,
        name='answer'),
    url(r'^svar/$', answer, name='answers'),
    url(r'^taggar/$', tags, name='tags'),
    url(r'^taggar/(?P<tag_name>.+)/$', tag, name='tag'),
    url(r'^quiz/$', quizzes, name='quizzes'),
    url(r'^quiz/resultat/$', save_quiz_results, name='save_quiz'),
    url(r'^quiz/resultat/(?P<quiz_result_id>[a-z0-9]+)/$', quiz_results,
        name='quiz_results'),
    url(r'^quiz/resultat/(?P<quiz_result_id>[a-z0-9]+)/img.jpg$', graph_image,
        name='graph_image'),
    url(r'^quiz/(?P<quiz_name>.+)/$', quiz, name='quiz'),
    url(r'^sök/$', search, name='search'),
    url(r'^kontakt/$', contact, name='contact'),
    url(r'^om/$', about, name='about'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
]

if settings.ADMIN_ENABLED:
    urlpatterns += [
        url(r'^admin/question/add', add_question, name='add_question'),
        url(r'^admin/question/delete/(?P<question_id>.+)$', delete_question,
            name='delete_question'),
        url(r'^admin/question/edit/(?P<question_id>.+)$', edit_question,
            name='edit_question'),
        url(r'^admin/party/add', add_party, name='add_party'),
        url(r'^admin/party/delete/(?P<party_id>.+)$', delete_party,
            name='delete_party'),
        url(r'^admin/party/edit/(?P<quiz_id>.+)$', edit_party,
            name='edit_party'),
        url(r'^admin/quiz/add', add_quiz, name='add_quiz'),
        url(r'^admin/quiz/delete/(?P<quiz_id>.+)$', delete_quiz,
            name='delete_quiz'),
        url(r'^admin/quiz/edit/(?P<quiz_id>.+)$', edit_quiz, name='edit_quiz'),
        url(r'^admin/tag/add', add_tag, name='add_tag'),
        url(r'^admin/tag/delete/(?P<tag_id>.+)$', delete_tag,
            name='delete_tag'),
        url(r'^admin/tag/edit/(?P<tag_id>.+)$', edit_tag, name='edit_tag'),
        url(r'^admin/answer/add/(?P<question_id>.+)$', add_answer,
            name='add_answer'),
        url(r'^admin/answer/delete/(?P<answer_id>.+)$', delete_answer,
            name='add_answer'),
        url(r'^admin/answer/edit/(?P<answer_id>.+)$', edit_answer,
            name='edit_answer'),
        url(r'^admin/$', admin_index, name='admin'),
        url(r'^admin/stuff/$', stuff, name='stuff'),
        url(r'^admin/handle/(?P<stuff_id>.+)$', handle, name='handle'),
        url(r'^django-admin/', admin.site.urls, name='admin'),
    ]
