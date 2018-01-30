from django.contrib import admin
from .models import Question, Quiz, Party, Answer, AnswerType, Feedback, QuizResultsInfo, QuizResults, Tag, QuestionTags, QuestionQuizzes


class TagsInline(admin.TabularInline):
    model = QuestionTags


class AnswersInline(admin.TabularInline):
    model = Answer


class QuestionQuizzesInline(admin.TabularInline):
    model = QuestionQuizzes


class QuestionTagsInline(admin.TabularInline):
    model = QuestionTags


class QuestionAdmin(admin.ModelAdmin):
    inlines = [TagsInline, AnswersInline]


class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionQuizzesInline]


class TagAdmin(admin.ModelAdmin):
    inlines = [QuestionTagsInline]


# Register your models here.
admin.site.register(Question, QuestionAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Party)
admin.site.register(Answer)
admin.site.register(AnswerType)
admin.site.register(Feedback)
admin.site.register(QuizResultsInfo)
admin.site.register(QuizResults)
admin.site.register(Tag, TagAdmin)
