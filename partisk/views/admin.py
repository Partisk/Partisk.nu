from django.contrib.auth.decorators import permission_required
from partisk.models import Stuff, Question, Answer
from partisk.forms import QuestionModelForm, StuffModelForm, AnswerModelForm
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse
import bleach


def login(request):
    pass


def logout(request):
    pass


def handle(request):
    obj = Stuff.objects.filter(handled=False).first()
    return redirect(reverse('stuff_detail',
                    kwargs={'pk': obj.id}))


def stuff(request):
    stuff = Stuff.objects.filter(handled=False).order_by('-date', 'id')
    context = {
        'stuff': stuff[:50],
        'total': stuff.count(),
    }
    return render(request, 'admin/stuff.html', context)


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


@permission_required('partisk.edit_stuff')
def stuff_done(request, stuff_id):
    stuff = get_object_or_404(Stuff, id=stuff_id)
    stuff.handled = True
    stuff.save()

    return redirect('handle')


def admin_index(request):
    return render(request, 'admin/admin.html')
