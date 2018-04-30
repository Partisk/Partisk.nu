from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from partisk.utils import get_tags_for_question
from partisk.models import Stuff, Question, Answer
from partisk.forms import QuestionModelForm, StuffModelForm, AnswerModelForm, ApproveAnswerModelForm, ApproveQuestionModelForm
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse
import bleach
        

def login(request):
    pass


@login_required
def logout(request):
    pass


@login_required
def handle(request):
    obj = Stuff.objects.filter(handled=False).first()
    return redirect(reverse('stuff_detail',
                    kwargs={'pk': obj.id}))


@login_required
def stuff(request):
    stuff = Stuff.objects.filter(handled=False).order_by('-date', 'id')
    context = {
        'stuff': stuff[:50],
        'total': stuff.count(),
    }
    return render(request, 'admin/stuff.html', context)


class StuffDetail(PermissionRequiredMixin, DetailView):
    model = Stuff
    template_name = 'admin/stuff_detail.html'
    permission_required = 'partisk.edit_stuff'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['total'] = Stuff.objects.filter(handled=False).count()
        context['question_form'] = QuestionModelForm(
            #initial={'tags': self.object.tags}
        )

        context['answer_form'] = AnswerModelForm(
            initial={
                'party': self.object.parties.first(),
                'stuff': self.object,
                'date': self.object.date,
                'source': self.object.url,
            }
        )
        context['answers'] = Answer.objects.filter(stuff_id=self.object.id, deleted=False)

        return context


@login_required
def approve_answers(request):
    obj = Answer.objects.filter(approved=False, deleted=False).order_by('id').first()
    return redirect(reverse('approve_answer_detail',
                    kwargs={'pk': obj.id}))


@login_required
def approve_questions(request):
    obj = Question.objects.filter(approved=False, deleted=False).order_by('id').first()
    return redirect(reverse('approve_question_detail',
                    kwargs={'pk': obj.id}))


class ApproveAnswerDetail(PermissionRequiredMixin, UpdateView):
    model = Answer
    permission_required = 'partisk.edit_answer'
    template_name = 'admin/approve_answer_detail.html'
    form_class = ApproveAnswerModelForm

    def get_success_url(self):
        return reverse('approve_answers')

    def get_context_data(self, **kwargs):
        context = super(ApproveAnswerDetail, self).get_context_data(**kwargs)
        context['total'] = Answer.objects.filter(approved=False, deleted=False).count()
        return context


class ApproveQuestionDetail(PermissionRequiredMixin, UpdateView):
    model = Question
    permission_required = 'partisk.edit_question'
    template_name = 'admin/approve_question_detail.html'
    form_class = ApproveQuestionModelForm

    def get_success_url(self):
        return reverse('approve_questions')

    def get_context_data(self, **kwargs):
        context = super(ApproveQuestionDetail, self).get_context_data(**kwargs)
        tags_data = get_tags_for_question(self.object.id)
        context['question_tags_string'] = ', '.join([tag.name for tag in tags_data])
        context['total'] = Question.objects.filter(approved=False, deleted=False).count()

        return context

    def get_form_kwargs(self):
        kwargs = super(ApproveQuestionDetail, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PartyExportList(ListView):
    model = Question
    template_name = 'admin/export_parties.html'
    
    def get_queryset(self):
        return Question.objects.filter(approved=True, deleted=False)
        

@login_required
@permission_required('partisk.edit_stuff')
def stuff_done(request, stuff_id):
    stuff = get_object_or_404(Stuff, id=stuff_id)
    stuff.handled = True
    stuff.save()

    return redirect('handle')


@login_required
@permission_required('partisk.edit_answer')
def approve_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    answer.approved = True
    answer.save()

    return redirect('approve_answers')


@login_required
@permission_required('partisk.edit_question')
def approve_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.approved = True
    question.save()

    return redirect('approve_questions')


@login_required
def admin_index(request):
    return render(request, 'admin/admin.html')
