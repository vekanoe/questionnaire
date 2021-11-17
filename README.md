#### Разворот приложения:

перейти в папку проекта
 
    cd questionnaire


создать файл с локальными настройками

    touch main/locals2.py


разместить в нём код

    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'questionnaire_db',
            'USER': 'q_user',
            'PASSWORD': '123456',
            'HOST': 'db',
        }
    }

создать/запустить контейнеры

    docker-compose up -d  --build


запустить миграции
 
    docker-compose exec web python manage.py migrate


собрать статику

    docker-compose exec web python manage.py collectstatic

создать суперпользователя

    docker-compose exec web python manage.py createsuperuser

запуск сервера

    docker-compose exec -d web python manage.py runserver 0.0.0.0:8000


#### Админка для администратора системы:

Создание и заполнение опросников дополнительно выведено в стандартную админку Django

/admin/questionnaire/questionnaire/1/change/


Через миграции устанавливаются презаполненные данные - 3 опросника с вопросами и ответами.


#### Функционал для администратора системы:

*Функционал администратора доступен только суперпользователям.*

1. Аутентификация в API для администратора

    1.1 /api/admin/login/ - залогиниться
    
    1.2 /api/admin/logout/ - разлогиниться

2. Опросники

    2.1 /api/admin/questionnaire/, метод GET - список опросников
 
    - Сортировка по Дате окончания проведения опроса
    - Добавлена фильтрация по Наименованию, Описанию, Датам старта и окончания проведения опроса
    - Добавлена пагинация (отображается 2 опросника на странице)

    2.2 /api/admin/questionnaire/, метод POST - создать опросник
    
    - Обязательные поля: Наименование, Дата старта и Дата окончания. Не обязательное: Описание.
    - Валидация полей: Дата старта должна быть меньше Даты окончания
        
            Пример данных:
            {
                "name": "Анкета покупателя",
                "start_date": "2021-11-16 20:57:53",
                "finish_date": "2021-12-16 20:57:53",
                "description": ""
            }
        
    2.3 /api/admin/questionnaire/<id_опросника>/, метод GET - отображение всех данных опросника вместе с вопросами и вариантами ответов на них

    2.4 /api/admin/questionnaire/<id_опросника>/, метод PATCH - изменение параметров опросника: Наименование, Описание, Даты старта и окончания. Вопросы и варианты ответов в данном запросе не редактируются.
        
    - Дата начала недоступна для редактирования
    - Валидация полей: Дата старта должна быть меньше Даты окончания. Запрещено вносить изменения в опросник в период его проведения.

            Пример данных:
            {
                "name": "Анкета покупателя 2",
                "finish_date": "2021-12-16 20:57:53"
            }

    2.5 /api/admin/questionnaire/<id_опросника>/, метод DELETE - удаление опросника
    
    - Удалить можно любой опросник, даже если он в активном периоде. Все данные, связанные с ним, в том числе ответы респондентов, будут удалены.

3. Вопросы из опросника

    3.1 /api/admin/question/, метод POST - создать вопрос вместе с вариантами возможных ответов

    - Используемые типы вопросов:
        - 0: 'ответ текстом'
        - 1: 'ответ с выбором одного варианта'
        - 2: 'ответ с выбором нескольких вариантов'
    - Обязательность ответа на вопрос: true/false
    - Валидация полей: соответствие типа вопроса перечню возможных ответов. Для 0 необходимо указать пустой список, для 1 и 2 список с ответами. 

            Пример данных:
            {
                "quest": 1,                  # id опросника
                "q_text": "Ваше имя?",       # текст вопроса
                "q_type": 0,                 # тип вопроса: ответ текстом
                "required": true,            # обязательно отвечать на вопрос при прохождении опросника или нет
                "answers": []                
            }
        
            {
                "quest": 1,                  # id опросника
                "q_text": "Пол?",            # текст вопроса
                "q_type": 1,                 # тип вопроса: выбор одного варианта
                "required": true,            # обязательно отвечать на вопрос при прохождении опросника или нет
                "answers": [                 # варианты ответов на вопрос
                    {"a_text": "Мужской"},
                    {"a_text": "Женский"}
                ]
            }

    3.2 /api/admin/question/<id_вопроса>/, метод GET - отображение данных вопроса и вариантов ответа к нему

    3.3 /api/admin/question/<id_вопроса>/, метод PATCH - изменение данных вопроса и обновление списка возможных ответов (предыдущие удаляются и сохраняется список из запроса)
    
    - Вопросы недоступны для редактирования в период проведения опроса
    - Валидация полей: соответствие типа вопроса перечню возможных ответов.

            Пример данных:
            {
                "q_text": "Ваше имя?",       # текст вопроса
                "q_type": 0,                 # тип вопроса: ответ текстом
                "required": true,            # обязательно отвечать на вопрос при прохождении опросника или нет
                "answers": []                
            }

    3.4 /api/admin/question/<id_вопроса>/, метод DELETE - удаление вопроса и вариантов ответа к нему
    
    - Вопросы недоступны для удаления в период проведения опроса


***

#### Функционал для респондента:

*Поскольку аутентификация для респондентов не предусмотрена в тз, в качестве ID используется UUID.*

1. /api/get_respondent_id/, метод POST - получить UUID респондента. Его необходимо сохранить, т.к. он используется в некоторых запросах далее.

    - Данные в запрос не передаются

2. /api/active_questionnaire/, метод GET - получить список активных опросников. 

    - Сортировка по Дате окончания проведения опроса
    - Добавлена фильтрация по Наименованию, Описанию, Датам старта и окончания проведения опроса
    - Добавлена пагинация (отображается 2 опросника на странице)

3. /api/questionnaire/<id_опросника>/, метод GET - получить данные опросника с вопросами и вариантами ответов.

    - Отображаются только активные опросники

4. /api/questionnaire_passing/, метод POST - отправить ответы респондента на опрос

    - Валидация: 
        - для data_filled важен формат данных: <текст_ответа> строка, даже если в качестве ответа используется число, <id_ответа> - тип int, <список_с_id_ответов> - список элементов типа int. Если формат нарушен, запрос не будет выполнен по ошибке валидации
        - проверяется обязательность заполнения поля (указана в настройках вопросов)
        - проверяется соответствие ответов респондента указанным возможным ответам на вопрос - рандомные id ответов вызывают ошибку валидации
        - нельзя пройти опрос с завершённым периодом проведения опроса

            Пример данных:
            {
                "respondent": "397645e7-1f6a-4449-88a6-2fda767c5dbb",     # UUID респондента
                "quest": 1,                                               # id опросника
                "data_filled": {"1": 1, "2": "Иван Петров", "3": [5, 6]}  # ответы на вопросы в формате {<id_вопроса>: <id_ответа>} или {<id_вопроса>: <текст_ответа>} или {<id_вопроса>: <список_с_id_ответов>}
            }

5. /api/questionnaire_passing/<id_прохождения_опросника>/, метод PATCH - заново пройти уже пройденный опросник. Данные предыдущего прохода не хранятся.

    - Валидация: 
        - проверка соответствия UUID респондента из запроса и UUID респондента ранее пройденного опроса.
        - нельзя пройти опрос с завершённым периодом проведения опроса

                Пример данных:
                {
                    "respondent": "397645e7-1f6a-4449-88a6-2fda767c5dbb",     # UUID респондента
                    "data_filled": {"1": 1, "2": "Иван Сидоров", "3": [5]}    # ответы на вопросы в формате {<id_вопроса>: <id_ответа>} или {<id_вопроса>: <текст_ответа>} или {<id_вопроса>: <список_с_id_ответов>}
                }

6. /api/respondent_passing/<uuid:pk>/, метод GET - получение пройденных пользователем опросов с детализацией по ответам (что выбрано)

    - отображаются все пройденные опросники, в том числе неактивные
