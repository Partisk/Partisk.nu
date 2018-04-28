from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from datetime import date


def get_slug(self, s):
    return s.lower().replace(" ", "_")


def from_slug(slug):
    return slug.replace("_", " ")


class AnswerType(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    answer = models.CharField(max_length=20)

    class Meta:
        db_table = 'answer_type'

    def __str__(self):
        return self.answer


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    party = models.ForeignKey('Party', on_delete=models.SET_NULL, null=True)
    answer_type = models.ForeignKey('AnswerType', related_name="+", on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, null=True)
    source = models.TextField(default=None, null=True)
    date = models.DateTimeField()
    created_by = models.IntegerField(default=None, null=True)
    deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_by = models.IntegerField(default=None, null=True)
    stuff = models.ForeignKey('Stuff', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'answers'

    def __str__(self):
        return str(self.id)


class Feedback(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    text = models.TextField()
    ip = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    referer = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feedback'

    def __str__(self):
        return self.text


class Party(models.Model):
    id = models.AutoField(primary_key=True, max_length=20)
    name = models.CharField(max_length=80)
    website = models.CharField(max_length=100)
    twitter = models.CharField(max_length=100, null=True, default=None)
    color = models.TextField()
    created_by = models.IntegerField(default=None, null=True)
    deleted = models.IntegerField(default=False)
    last_result_parliment = models.DecimalField(max_digits=10,
                                                decimal_places=2,
                                                default=0)
    last_result_eu = models.DecimalField(max_digits=10, decimal_places=2,
                                         default=0)
    updated_by = models.IntegerField(blank=True, null=True, default=None)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    short_name = models.CharField(max_length=5, blank=True, null=True)
    created_by = models.IntegerField(default=None, null=True)

    def _get_slug(self):
        return get_slug(self, self.name)

    slug = property(_get_slug)

    class Meta:
        db_table = 'parties'

    def __str__(self):
        return self.name


class QuestionQuizzes(models.Model):
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, null=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'question_quizzes'


class QuestionTags(models.Model):
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, null=True)
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'question_tags'


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    approved_date = models.DateTimeField(auto_now_add=True)
    done = models.BooleanField(default=False)
    version = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', through='QuestionTags', blank=True)

    created_by = models.IntegerField(default=None, null=True)

    def _get_slug(self):
        return get_slug(self, self.title)

    slug = property(_get_slug)

    class Meta:
        db_table = 'questions'
        ordering = ['title']

    def __str__(self):
        return self.title

    def save_model(self, request, question, form, change):
        question.save()
        print (form.cleaned_data)
        print (question)
        print (request)
        add_tags(self.tags_string, question, self.user, True)


class QuizAnswer(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    answer_type = models.ForeignKey('AnswerType', on_delete=models.SET_NULL, null=True)
    quiz_results_info = models.ForeignKey('QuizResultsInfo', on_delete=models.SET_NULL, null=True)
    importance = models.IntegerField()

    class Meta:
        db_table = 'quiz_answers'


class QuizResultsInfo(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=date.today)
    country = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    postal_code = models.CharField(max_length=40)
    coordinates = models.CharField(max_length=40)
    accuracy = models.IntegerField()
    subdivision = models.CharField(max_length=40)
    kommun = models.ForeignKey('Kommun', on_delete=models.SET_NULL, null=True)
    lan = models.ForeignKey('Lan', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'quiz_results_info'

    def __str__(self):
        return self.id


class QuizResults(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    data = models.TextField()
    created = models.DateField(default=date.today)
    version = models.IntegerField()
    quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'quiz_results'

    def __str__(self):
        return self.id


class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    approved_date = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=None, null=True)

    def _get_slug(self):
        return get_slug(self, self.name)

    slug = property(_get_slug)

    class Meta:
        db_table = 'quizzes'

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=None, null=True)
    is_category = models.NullBooleanField(blank=True)
    created_by = models.IntegerField(default=None, null=True)
    updated_by = models.IntegerField(default=None, null=True)

    def _get_slug(self):
        return get_slug(self, self.name)

    slug = property(_get_slug)

    class Meta:
        db_table = 'tags'

    def __str__(self):
        return self.name


class Kommun(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, null=True)
    lan = models.CharField(max_length=2)

    class Meta:
        db_table = 'kommuner'

    def __str__(self):
        return self.name


class Lan(models.Model):
    id = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=40, null=True)

    class Meta:
        db_table = 'lan'

    def __str__(self):
        return self.name


class SourceType(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'source_type'

    def __str__(self):
        return self.name


class Source(models.Model):
    id = models.AutoField(primary_key=True)
    source_type = models.ForeignKey('SourceType', related_name="+", on_delete=models.SET_NULL, null=True)
    name = models.TextField(null=True)
    content = models.TextField(null=True)
    last_updated = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'source'

    def __str__(self):
        return self.id


class Stuff(models.Model):
    id = models.AutoField(primary_key=True)
    source_type = models.ForeignKey('SourceType', related_name="+", on_delete=models.SET_NULL, null=True)
    url = models.TextField(null=True)
    title = models.CharField(max_length=400)
    content = models.TextField(null=True)
    parties = models.ManyToManyField('Party', blank=True)
    content_hash = models.CharField(max_length=32, blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    date = models.DateTimeField(blank=True, null=True)
    handled = models.BooleanField(default=False)

    class Meta:
        db_table = 'stuff'

    def __str__(self):
        return str(self.id) + " " + self.title
