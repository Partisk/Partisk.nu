from django import forms

from partisk.models import Answer, Party, Question, Quiz, Tag


class AnswerSaveModelForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_type', 'party', 'source', 'date', 'description',
                  'question')


class AnswerModelForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_type', 'party', 'source', 'date', 'description')


class PartyModelForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name', 'website', 'color', 'description', 'short_name')


class QuestionModelForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'description')


class QuizModelForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('name', 'description')


class TagModelForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name',)

