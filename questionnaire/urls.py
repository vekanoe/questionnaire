from django.urls import path, include

from .views_admin import APIQuestionnaire, APIQuestionnaireListCreate, APIQuestionCreate, APIQuestion
from .views_respondent import APIRespondentCreate, APIActiveQuestionnaireList, APIQuestionnaireRetrieve, \
    APIQuestionnairePassing, APIQuestionnaireRePassing, APIRespondentPassing

urlpatterns = [

    # функционал администратора системы
    path('admin/', include('rest_framework.urls')),
    path('admin/questionnaire/', APIQuestionnaireListCreate.as_view(), name='questionnaire-list-create'),
    path('admin/questionnaire/<int:pk>/', APIQuestionnaire.as_view(), name='questionnaire-management'),
    path('admin/question/', APIQuestionCreate.as_view(), name='question-create'),
    path('admin/question/<int:pk>/', APIQuestion.as_view(), name='question-management'),

    # функционал для респондента
    path('get_respondent_id/', APIRespondentCreate.as_view(), name='respondent-create'),
    path('active_questionnaire/', APIActiveQuestionnaireList.as_view(), name='active-questionnaire-list'),
    path('questionnaire/<int:pk>/', APIQuestionnaireRetrieve.as_view(), name='questionnaire-retrieve'),
    path('questionnaire_passing/', APIQuestionnairePassing.as_view(), name='questionnaire_passing'),
    path('questionnaire_passing/<int:pk>/', APIQuestionnaireRePassing.as_view(), name='questionnaire_repassing'),
    path('respondent_passing/<uuid:pk>/', APIRespondentPassing.as_view(), name='respondent-passing'),
]
