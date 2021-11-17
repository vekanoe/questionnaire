from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, DateTimeFromToRangeFilter

from .models import Questionnaire


class QuestionnaireFilter(FilterSet):
    """ Фильтр по Опросникам """

    name = CharFilter(lookup_expr='icontains')
    start_date = DateTimeFromToRangeFilter()
    finish_date = DateTimeFromToRangeFilter()
    description = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Questionnaire
        fields = ['name', 'start_date', 'finish_date', 'description']
