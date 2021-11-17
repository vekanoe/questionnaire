from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, UpdateAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Questionnaire, Question
from .serializers import QuestionnaireSerializer, QuestionnaireWithQASerializer, \
    QuestionCreateSerializer, QuestionSerializer
from .filters import QuestionnaireFilter


class APIQuestionnaireListCreate(ListCreateAPIView):
    """ Список опросников, Создание опросника """

    serializer_class = QuestionnaireSerializer
    queryset = Questionnaire.objects.all()
    permission_classes = [IsAdminUser]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = QuestionnaireFilter


class APIQuestionnaire(RetrieveUpdateDestroyAPIView):
    """ Отображение / изменение / удаление опросника """

    serializer_class = QuestionnaireWithQASerializer
    queryset = Questionnaire.objects.all()
    permission_classes = [IsAdminUser]


class APIQuestionCreate(CreateAPIView):
    """ Добавление вопроса в опросник вместе с вариантами ответов """

    serializer_class = QuestionCreateSerializer
    permission_classes = [IsAdminUser]


class APIQuestion(RetrieveUpdateDestroyAPIView):
    """ Отображение / изменение / удаление вопроса и вариантов ответов """

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.quest.start_date < timezone.now() < instance.quest.finish_date:
            return Response('Нельзя удалять вопросы в период проведения опроса.', status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
