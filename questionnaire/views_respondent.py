from django.utils import timezone

from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, UpdateAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Questionnaire, QuestionnairePassing, Respondent
from .serializers import QuestionnaireSerializer, RespondentCreateSerializer, \
    QuestionnairePassingSerializer, QuestionnaireRePassingSerializer, RespondentPassingSerializer, \
    QuestionnaireWithQASerializer
from .filters import QuestionnaireFilter


class APIRespondentCreate(CreateAPIView):
    """ Добавить в систему респондента """

    serializer_class = RespondentCreateSerializer


class RespondentQuestionnaireMixin:
    """ Респонденты имеют доступ только к активным опросникам """

    def get_queryset(self):
        now = timezone.now()
        return Questionnaire.objects.filter(start_date__lt=now, finish_date__gt=now)


class APIActiveQuestionnaireList(RespondentQuestionnaireMixin, ListAPIView):
    """ Список активных опросников """

    serializer_class = QuestionnaireSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = QuestionnaireFilter


class APIQuestionnaireRetrieve(RespondentQuestionnaireMixin, RetrieveAPIView):
    """ Отобразить опросник с вопросами и ответами """

    serializer_class = QuestionnaireWithQASerializer


class APIQuestionnairePassing(CreateAPIView):
    """ Пройти опросник """

    serializer_class = QuestionnairePassingSerializer


class APIQuestionnaireRePassing(UpdateAPIView):
    """ Перепройти опросник """

    serializer_class = QuestionnaireRePassingSerializer
    queryset = QuestionnairePassing.objects.all()


class APIRespondentPassing(ListAPIView):
    """ Список активных опросников """

    serializer_class = RespondentPassingSerializer
    queryset = Respondent.objects.all()
