from django.utils import timezone
from rest_framework import serializers
from rest_framework import exceptions

from .models import Questionnaire, Question, Answer, Respondent, QuestionnairePassing


class QuestionnaireSerializer(serializers.ModelSerializer):
    """ Опросник """

    class Meta:
        model = Questionnaire
        fields = ['id', 'name', 'start_date', 'finish_date', 'description']

    def validate(self, data):

        super().validate(data)

        b_date = data.get('start_date')
        e_date = data.get('finish_date')

        if b_date and e_date and b_date >= e_date:
            raise exceptions.ValidationError(
                {'start_date': 'Дата завершения проведения опроса должна превышать дату его начала.'})

        return data


class AnswerListSerializer(serializers.ModelSerializer):
    """ Ответы на вопросы """

    class Meta:
        model = Answer
        fields = ['id', 'a_text']
        extra_kwargs = {'id': {'read_only': True}}


class QuestionListSerializer(serializers.ModelSerializer):
    """ Вопросы """

    answers = AnswerListSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'q_text', 'q_type', 'required', 'answers']
        extra_kwargs = {'id': {'read_only': True}}


class QuestionnaireWithQASerializer(serializers.ModelSerializer):
    """ Опросник с отображением вопросов и вариантов ответов """

    questions = QuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = ['id', 'name', 'start_date', 'finish_date', 'description', 'questions']
        extra_kwargs = {'id': {'read_only': True}, 'start_date': {'read_only': True}}

    def get_questions(self, obj):
        results = []
        for q in obj.questions.prefetch_related('answers').all():
            results.append({
                'q_text': q.q_text, 'q_type': q.q_type, 'required': q.required,
                'answers': [a.a_text for a in q.answers.all()]})

        return results

    def validate(self, data):

        super().validate(data)

        b_date = data.get('start_date', None) or self.instance.start_date
        e_date = data.get('finish_date', None) or self.instance.finish_date

        if b_date >= e_date:
            raise exceptions.ValidationError(
                {'start_date': 'Дата завершения проведения опроса должна превышать дату его начала.'})

        if self.context['request'].stream.method in ('PATCH', 'PUT') and e_date < timezone.now() < b_date:
            raise exceptions.ValidationError(
                {'start_date': 'Нельзя изменять опросник в период его проведения.'})

        return data


class QuestionCreateSerializer(serializers.ModelSerializer):
    """ Создать вопрос в опросник вместе с вариантами ответов """

    answers = AnswerListSerializer(many=True)

    class Meta:
        model = Question
        fields = ['quest', 'q_text', 'q_type', 'required', 'answers']

    def validate(self, data):

        super().validate(data)

        q_type = data.get('q_type')
        answers = data.get('answers')

        if q_type == Question.Q_TYPE_TEXT and answers:
            raise exceptions.ValidationError(
                {'q_type': 'Для типа вопроса "ответ текстом" не предусмотрен список ответов. Укажите пустой список.'})

        if q_type != Question.Q_TYPE_TEXT and not answers:
            raise exceptions.ValidationError(
                {'q_type': 'Данный тип вопроса предусматривает список ответов. Перечислите их в качестве списка.'})

        return data

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        instance = Question.objects.create(**validated_data)

        if answers:
            Answer.objects.bulk_create([Answer(question=instance, **a) for a in answers])

        return instance


class QuestionSerializer(serializers.ModelSerializer):
    """ Вопросы """

    answers = AnswerListSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'q_text', 'q_type', 'required', 'answers']
        extra_kwargs = {'id': {'read_only': True},}

    def validate(self, data):

        super().validate(data)

        if self.instance.quest.start_date < timezone.now() < self.instance.quest.finish_date:
            raise exceptions.ValidationError(
                {'start_date': 'Нельзя изменять вопросы в период проведения опроса.'})

        q_type = data.get('q_type')
        answers = data.get('answers')

        if q_type == Question.Q_TYPE_TEXT and answers:
            raise exceptions.ValidationError(
                {'q_type': 'Для типа вопроса "ответ текстом" не предусмотрен список ответов. Укажите пустой список.'})

        if q_type != Question.Q_TYPE_TEXT and not answers:
            raise exceptions.ValidationError(
                {'q_type': 'Данный тип вопроса предусматривает список ответов. Перечислите их в качестве списка.'})

        return data

    def update(self, instance, validated_data):
        answers = validated_data.pop('answers')
        instance = super().update(instance, validated_data)

        if answers:
            instance.answers.all().delete()
            Answer.objects.bulk_create([Answer(question=instance, **a) for a in answers])

        return instance


class RespondentCreateSerializer(serializers.ModelSerializer):
    """ Респондент """

    class Meta:
        model = Respondent
        fields = ['id']
        extra_kwargs = {'id': {'read_only': True}, }


class BaseQuestionnairePassingSerializer(serializers.ModelSerializer):
    """ Базовый класс для прохождения опросника """

    data_filled = serializers.JSONField()

    class Meta:
        model = QuestionnairePassing

    def _validate_data_filled(self, datas, quest):
        """ Проверка ответов """

        now = timezone.now()
        if now < quest.start_date or now > quest.finish_date:
            raise exceptions.ValidationError(
                {'start_date': 'Нельзя пройти опросник с завершённым периодом проведения.'})

        if type(datas) != dict or not datas:
            raise exceptions.ValidationError({'data_filled': "Необходимо указать данные в json-формате"})

        qs = Question.objects.filter(quest=quest).prefetch_related('answers')

        not_specified = []  # нет ответа на обязательный вопрос
        wrong_format = []  # неверный формат ответа

        def get_datas(x, q_type):
            d = datas.get(x, None)
            if d:
                type_user_answers = type(d)
                if q_type == Question.Q_TYPE_TEXT and type_user_answers != str \
                    or q_type == Question.Q_TYPE_SINGLE and type_user_answers != int \
                    or q_type == Question.Q_TYPE_SET and (type_user_answers != list or len([i for i in d if type(i) == int]) != len(d)):
                        wrong_format.append(x)
            return d

        q_table = [(q.id, q.q_type, q.required, list(q.answers.values_list('id', flat=True)), get_datas(str(q.id), q.q_type)) for q in qs]

        if wrong_format:
            raise exceptions.ValidationError({'data_filled': f'Ответы для следующих вопросов были указаны в неверном формате: {", ".join(wrong_format)}'})

        not_in_answers_list = []  # в ответе приведены посторонние данные, которых нет в предложенных ответах
        for id, q_type, required, answers, user_answers in q_table:
            if user_answers:
                if q_type == Question.Q_TYPE_SINGLE and user_answers not in answers or q_type == Question.Q_TYPE_SET and not (set(user_answers) < set(answers)):
                    not_in_answers_list.append(str(id))
            elif required:
                not_specified.append(str(id))

        error_str = []
        if not_specified:
            error_str.append(f'На следующие обязательные вопросы не были указаны ответы: {", ".join(not_specified)}')
        if not_in_answers_list:
            error_str.append(f'Для следующих вопросов были указаны посторонние данные, которых нет в предложенных ответах: {", ".join(not_in_answers_list)}')

        if error_str:
            raise exceptions.ValidationError({'data_filled': " ".join(error_str)})


class QuestionnairePassingSerializer(BaseQuestionnairePassingSerializer):
    """ Ответы респондента на опросник """

    class Meta(BaseQuestionnairePassingSerializer.Meta):
        fields = ['respondent', 'quest', 'data_filled']

    def validate(self, data):

        super().validate(data)
        self._validate_data_filled(data.get('data_filled'), data.get('quest'))

        return data


class QuestionnaireRePassingSerializer(BaseQuestionnairePassingSerializer):
    """ Повторное прохождение опросника: Ответы респондента на опросник """

    class Meta(BaseQuestionnairePassingSerializer.Meta):
        fields = ['respondent', 'data_filled']
        extra_kwargs = {'respondent': {'write_only': True}}

    def validate(self, data):

        super().validate(data)

        respondent = data.get('respondent', None)

        if respondent != self.instance.respondent:
            raise exceptions.ValidationError({'respondent': "Вы не имеете права редактировать ответы на этот опрос."})

        self._validate_data_filled(data.get('data_filled'), self.instance.quest)

        return data


class QPForRespondentSerializer(serializers.ModelSerializer):
    """ Ответы на вопросы """

    quest = QuestionnaireSerializer()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = QuestionnairePassing
        fields = ['id', 'pass_date', 'quest', 'questions']

    def get_questions(self, obj):

        answers = eval(obj.data_filled)
        answer_ids = []
        for k, v in answers.items():
            type_v = type(v)
            if type_v == int:
                answer_ids.append(v)
            elif type_v == list:
                answer_ids += v
        answer_dict = {a.question.id: {"id": a.id, "a_text": a.a_text} for a in Answer.objects.filter(id__in=answer_ids)}

        return [{
            "id": q.id,
            "q_text": q.q_text,
            "required": q.required,
            "answer": answer_dict.get(q.id, answers.get(str(q.id), None))
        } for q in obj.quest.questions.all()]


class RespondentPassingSerializer(serializers.ModelSerializer):
    """ Список пройденных опросников с ответами для респондента """

    questionnaire_passing = QPForRespondentSerializer(many=True)

    class Meta:
        model = Respondent
        fields = ['questionnaire_passing']
