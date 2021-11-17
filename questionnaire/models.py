import uuid
from django.db import models


class Respondent(models.Model):
    """ Респонденты """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = 'Анкетируемый пользователь'
        verbose_name_plural = 'Анкетируемые пользователи'


class Questionnaire(models.Model):
    """ Опросники """

    name = models.CharField('Наименование', max_length=128, null=False, blank=False)
    start_date = models.DateTimeField('Дата старта', null=False, blank=False)
    finish_date = models.DateTimeField('Дата окончания', null=False, blank=False)
    description = models.CharField('Описание', max_length=256, null=False, blank=True, default='')

    class Meta:
        verbose_name = 'Опросник'
        verbose_name_plural = 'Опросники'
        ordering = ('-finish_date',)

    def __str__(self):
        return f'{self.name}: {self.start_date} - {self.finish_date}'


class Question(models.Model):
    """ Вопросы опросника """

    # Типы вопросов
    Q_TYPE_TEXT = 0
    Q_TYPE_SINGLE = 1
    Q_TYPE_SET = 2
    Q_TYPES = (
        (Q_TYPE_TEXT, 'ответ текстом',),
        (Q_TYPE_SINGLE, 'ответ с выбором одного варианта',),
        (Q_TYPE_SET, 'ответ с выбором нескольких вариантов'),
    )

    quest = models.ForeignKey(Questionnaire, verbose_name='Опросник', on_delete=models.CASCADE, related_name='questions')

    q_text = models.CharField('Вопрос', max_length=256, null=False, blank=False)
    q_type = models.SmallIntegerField('Тип вопроса', choices=Q_TYPES, default=Q_TYPE_TEXT)
    required = models.BooleanField('Обязательный', default=False)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ('id', )

    def __str__(self):
        return f'{self.quest.name}: {self.q_text}'


class Answer(models.Model):
    """ Ответы на вопросы """

    question = models.ForeignKey(Question, verbose_name='Вопрос', on_delete=models.CASCADE, related_name='answers')
    a_text = models.CharField('Ответ', max_length=256, null=False, blank=False)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ('id', )

    def __str__(self):
        return f'{self.a_text}'


class QuestionnairePassing(models.Model):
    """ Ответы респондентов на вопросы опросника """

    respondent = models.ForeignKey(Respondent, verbose_name='Респондент', on_delete=models.CASCADE, related_name='questionnaire_passing')
    quest = models.ForeignKey(Questionnaire, verbose_name='Опросник', on_delete=models.CASCADE, related_name='+')
    data_filled = models.TextField('Ответы на вопросы', blank=False, null=False)

    pass_date = models.DateTimeField('Дата прохождения опросника', auto_now=True)

    class Meta:
        verbose_name = 'Ответы респондентов'
        verbose_name_plural = 'Ответы респондентов'
        unique_together = ('respondent', 'quest')
