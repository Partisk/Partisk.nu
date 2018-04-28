from django.contrib.auth.decorators import permission_required, login_required
from partisk.models import Stuff, Question, Answer
from partisk.forms import QuestionModelForm, StuffModelForm, AnswerModelForm, ApproveAnswerModelForm
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
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


@login_required
class StuffDetail(DetailView):
    model = Stuff
    template_name = 'admin/stuff_detail.html'

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
    obj = Answer.objects.filter(approved=False).first()
    return redirect(reverse('approve_answer_detail',
                    kwargs={'pk': obj.id}))


@login_required
class ApproveAnswerDetail(UpdateView):
    model = Answer
    template_name = 'admin/approve_answer_detail.html'
    form_class = ApproveAnswerModelForm

    def get_success_url(self):
        return reverse('approve_answers')


@login_required
@permission_required('partisk.edit_stuff')
def stuff_done(request, stuff_id):
    stuff = get_object_or_404(Stuff, id=stuff_id)
    stuff.handled = True
    stuff.save()

    return redirect('handle')


@login_required
def admin_index(request):
    return render(request, 'admin/admin.html')
