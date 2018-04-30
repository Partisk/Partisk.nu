from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, HTML, Layout, Div
from django.urls import reverse
from partisk.utils import add_tags

from partisk.models import Answer, Party, Question, Quiz, Tag, Stuff


class AnswerSaveModelForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_type', 'party', 'source', 'date', 'description',
                  'question', 'stuff')


class AnswerModelForm(forms.ModelForm):
    stuff = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(AnswerModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_action = '/admin/answer/add/'
        self.helper.layout = Layout(
            Div(
                HTML('<div class="col-form-label col-lg-2"></div>'),
                HTML('<div class="col-lg-8"><input id="question_autocomplete" class="form-control" type="text" /></div>'),
                css_class="form-group row"
            ),
            'question', 'answer_type', 'party', 'source', 'date', 'description', 'stuff'
        )
        self.helper.add_input(Submit('submit', 'Add answer'))

    class Meta:
        model = Answer
        fields = ('answer_type', 'party', 'source', 'date', 'description', 'question', 'stuff')


class ApproveAnswerModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ApproveAnswerModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        #self.helper.form_action = reverse('edit_answer', args={'answer_id': self.instance.id})
        self.helper.add_input(Submit('submit', 'Update answer'))

    class Meta:
        model = Answer
        fields = ('answer_type', 'party', 'source', 'date', 'description', 'question', 'outdated')


class ApproveQuestionModelForm(forms.ModelForm):
    tags_string = forms.TextInput()

    def __init__(self, user, *args, **kwargs):
        super(ApproveQuestionModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'title', 'description',
            Div(
                HTML('<label class="col-form-label col-lg-2">Tags</label>'),
                HTML('<div class="col-lg-8"><input name="tags_string" class="form-control" value="{{question_tags_string}}" type="text" /></div>'),
                css_class="form-group row"
            )
        )
        self.helper.add_input(Submit('submit', 'Update question'))
        self.user = user

    def save(self, commit=True):
        question = super(ApproveQuestionModelForm, self).save(commit=True)
        add_tags(self.data.get('tags_string'), question, self.user, True)

        return question

    class Meta:
        model = Question
        fields = ('title', 'description')


class PartyModelForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name', 'website', 'color', 'description', 'short_name')


class QuestionModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = '/admin/question/add'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'title', 'description',
            Div(
                HTML('<label class="col-form-label col-lg-2">Tags</label>'),
                HTML('<div class="col-lg-8"><input name="tags" class="form-control" type="text" /></div>'),
                css_class="form-group row"
            )
        )
        self.helper.add_input(Submit('submit', 'Add question'))

    class Meta:
        model = Question
        fields = ('title', 'description')


class StuffModelForm(forms.ModelForm):
    content = forms.CharField(required=False)
    title = forms.CharField(required=False)

    class Meta:
        model = Stuff
        fields = ('content', 'source_type', 'url', 'title')


class QuizModelForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('name', 'description')


class TagModelForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name',)

