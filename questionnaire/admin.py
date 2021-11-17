from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from .models import Questionnaire, Question, Answer


class AnswerFormSet(BaseInlineFormSet):
    def clean(self):
        super(AnswerFormSet, self).clean()

        forms_count = len([1 for form in self.forms if not form.cleaned_data.get('DELETE', False)])
        if self.instance.q_type in (Question.Q_TYPE_SET, Question.Q_TYPE_SINGLE) and forms_count == 0 or self.instance.q_type == Question.Q_TYPE_TEXT and forms_count > 0:
            raise ValidationError('Список возможных ответов не соответствует типу вопроса')


class AnswerInline(NestedTabularInline):
    """ Игроки Команд """

    model = Answer
    extra = 0
    actions = None
    is_sortable = False
    formset = AnswerFormSet


class QuestionInline(NestedTabularInline):
    """ Вопросы опросника """

    model = Question
    inlines = [AnswerInline]
    extra = 0
    actions = None
    is_sortable = False


@admin.register(Questionnaire)
class QuestionnaireAdmin(NestedModelAdmin):
    """ Опросники """

    list_display = ('name', 'start_date', 'finish_date')
    date_hierarchy = 'start_date'
    search_fields = ('name', )

    inlines = [QuestionInline]
