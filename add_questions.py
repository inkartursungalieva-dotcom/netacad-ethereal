import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Module, Question, Choice


def run():
    # Удаляем старые вопросы
    Question.objects.all().delete()
    Choice.objects.all().delete()

    # Данные вопросов для каждого модуля
    modules_questions = [
        # Модуль 1: Введение
        {
            'slug': 'introduction',
            'questions': [
                {
                    'text': 'Что такое компьютерная сеть?',
                    'text_kk': 'Компьютерлік желі дегеніміз не?',
                    'hint': 'Базовое определение сети.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Группа соединенных компьютеров для обмена данными', 'Деректермен алмасу үшін қосылған компьютерлер тобы', True),
                        ('Один мощный компьютер', 'Бір қуатты компьютер', False),
                        ('Программа для чата', 'Чатқа арналған бағдарлама', False),
                        ('Сервер для хранения файлов', 'Файлдарды сақтау үшін сервер', False)
                    ]
                },
                {
                    'text': 'Какая основная цель создания компьютерных сетей?',
                    'text_kk': 'Компьютерлік желілерді құрудың негізгі мақсаты қандай?',
                    'hint': 'Зачем вообще нужны сети?',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Обмен ресурсами и данными между устройствами', 'Құрылғылар арасында ресурстар мен деректерді алмасу', True),
                        ('Увеличение мощности одного компьютера', 'Бір компьютердің қуатын арттыру', False),
                        ('Создание игр', 'Ойындарды құру', False),
                        ('Хранение данных на одном устройстве', 'Деректерді бір құрылғыда сақтау', False)
                    ]
                },
                {
                    'text': 'Какой тип сети охватывает наибольшую территорию?',
                    'text_kk': 'Қандай желі түрі ең үлкен аймақты қамтиды?',
                    'hint': 'Глобальная сеть.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('LAN', 'LAN', False),
                        ('MAN', 'MAN', False),
                        ('WAN', 'WAN', True),
                        ('PAN', 'PAN', False)
                    ]
                },
                {
                    'text': 'Что такое топология сети?',
                    'text_kk': 'Желі топологиясы дегеніміз не?',
                    'hint': 'Структура соединения устройств.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Схема расположения устройств и соединений между ними', 'Құрылғылардың орналасқан схемасы және олар арасындағы байланыстар', True),
                        ('Скорость передачи данных', 'Деректерді беру жылдамдығы', False),
                        ('Тип сетевого оборудования', 'Желілік жабдықтың түрі', False),
                        ('Количество компьютеров в сети', 'Желідегі компьютерлер саны', False)
                    ]
                },
                {
                    'text': 'Какая топология представляет собой общую шину для всех устройств?',
                    'text_kk': 'Қандай топология барлық құрылғылар үшін жалпы шина болып табылады?',
                    'hint': 'Линейная структура.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Кольцевая', 'Жүйрек', False),
                        ('Звезда', 'Жұлдыз', False),
                        ('Шинная', 'Шина', True),
                        ('Сетчатая', 'Тор', False)
                    ]
                },
                {
                    'text': 'Что такое клиент-серверная архитектура?',
                    'text_kk': 'Клиент-сервер архитектурасы дегеніміз не?',
                    'hint': 'Разделение ролей.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Модель, где клиенты запрашивают услуги, а сервер предоставляет их', 'Клиенттер қызметтерді сұрайтын, ал сервер оларды ұсынатын модель', True),
                        ('Все компьютеры равноправны', 'Барлық компьютерлер тең құқықты', False),
                        ('Одна машина выполняет все функции', 'Бір машина барлық функцияларды орындайды', False),
                        ('Только для облачных сервисов', 'Тек бұлттық қызметтер үшін', False)
                    ]
                },
                {
                    'text': 'Какое устройство используется для соединения разных сетей?',
                    'text_kk': 'Әртүрлі желілерді қосу үшін қандай құрылғы қолданылады?',
                    'hint': 'Маршрутизатор.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Хаб', 'Хаб', False),
                        ('Маршрутизатор', 'Маршрутизатор', True),
                        ('Коммутатор', 'Коммутатор', False),
                        ('Модем', 'Модем', False)
                    ]
                },
                {
                    'text': 'Что означает аббревиатура LAN?',
                    'text_kk': 'LAN аббревиатурасы нені білдіреді?',
                    'hint': 'Локальная сеть.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Local Area Network', 'Local Area Network', True),
                        ('Large Area Network', 'Large Area Network', False),
                        ('Long Area Network', 'Long Area Network', False),
                        ('Local Access Network', 'Local Access Network', False)
                    ]
                },
                {
                    'text': 'Какая модель взаимодействия является эталоном для сетевых протоколов?',
                    'text_kk': 'Желілік протоколдар үшін эталон болып табылатын өзара әрекеттесу моделі қандай?',
                    'hint': '7 уровней.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('TCP/IP', 'TCP/IP', False),
                        ('OSI', 'OSI', True),
                        ('HTTP', 'HTTP', False),
                        ('DNS', 'DNS', False)
                    ]
                },
                {
                    'text': 'Что такое пропускная способность сети?',
                    'text_kk': 'Желінің өткізу қабілеті дегеніміз не?',
                    'hint': 'Количество данных в единицу времени.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Максимальное количество данных, передаваемое за единицу времени', 'Бір уақыт бірлігінде берілетін максималды деректер саны', True),
                        ('Расстояние между компьютерами', 'Компьютерлер арасындағы қашықтық', False),
                        ('Количество устройств в сети', 'Желідегі құрылғылар саны', False),
                        ('Время отклика', 'Жауап беру уақыты', False)
                    ]
                }
            ]
        },
        # Модуль 2: Модель OSI
        {
            'slug': 'osi_model',
            'questions': [
                {
                    'text': 'Сколько уровней в модели OSI?',
                    'text_kk': 'OSI моделіне қанша деңгей кіреді?',
                    'hint': 'От 1 до 7.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('5', '5', False),
                        ('6', '6', False),
                        ('7', '7', True),
                        ('8', '8', False)
                    ]
                },
                {
                    'text': 'Какой уровень отвечает за физическую передачу битов?',
                    'text_kk': 'Физикалық биттерді беруге қай деңгей жауап береді?',
                    'hint': 'Самый низкий уровень.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Канальный', 'Арналық', False),
                        ('Физический', 'Физикалық', True),
                        ('Сетевой', 'Желілік', False),
                        ('Транспортный', 'Көліктік', False)
                    ]
                },
                {
                    'text': 'На каком уровне работают коммутаторы?',
                    'text_kk': 'Коммутаторлар қай деңгейде жұмыс істейді?',
                    'hint': 'Уровень с MAC-адресами.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Физический', 'Физикалық', False),
                        ('Канальный', 'Арналық', True),
                        ('Сетевой', 'Желілік', False),
                        ('Транспортный', 'Көліктік', False)
                    ]
                },
                {
                    'text': 'Какой уровень отвечает за логическую адресацию и маршрутизацию?',
                    'text_kk': 'Логикалық адресация мен маршрутизацияға қай деңгей жауап береді?',
                    'hint': 'IP-адреса.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Канальный', 'Арналық', False),
                        ('Сетевой', 'Желілік', True),
                        ('Транспортный', 'Көліктік', False),
                        ('Прикладной', 'Қолданбалы', False)
                    ]
                },
                {
                    'text': 'Какой протокол работает на транспортном уровне?',
                    'text_kk': 'Көліктік деңгейде қандай протокол жұмыс істейді?',
                    'hint': 'TCP или UDP.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('IP', 'IP', False),
                        ('TCP', 'TCP', True),
                        ('HTTP', 'HTTP', False),
                        ('Ethernet', 'Ethernet', False)
                    ]
                },
                {
                    'text': 'На каком уровне происходит сессионное управление?',
                    'text_kk': 'Сессияларды басқару қай деңгейде жүріседі?',
                    'hint': 'Уровень сессий.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Транспортный', 'Көліктік', False),
                        ('Сессионный', 'Сессиялық', True),
                        ('Представления', 'Көрсету', False),
                        ('Прикладной', 'Қолданбалы', False)
                    ]
                },
                {
                    'text': 'Какой уровень отвечает за шифрование и представление данных?',
                    'text_kk': 'Деректерді шифрлау және көрсетуге қай деңгей жауап береді?',
                    'hint': 'Форматирование данных.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Сессионный', 'Сессиялық', False),
                        ('Представления', 'Көрсету', True),
                        ('Прикладной', 'Қолданбалы', False),
                        ('Транспортный', 'Көліктік', False)
                    ]
                },
                {
                    'text': 'На каком уровне работают веб-браузеры?',
                    'text_kk': 'Веб-браузерлер қай деңгейде жұмыс істейді?',
                    'hint': 'Самый высокий уровень.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Транспортный', 'Көліктік', False),
                        ('Сессионный', 'Сессиялық', False),
                        ('Прикладной', 'Қолданбалы', True),
                        ('Представления', 'Көрсету', False)
                    ]
                },
                {
                    'text': 'Что такое инкапсуляция в модели OSI?',
                    'text_kk': 'OSI моделінде инкапсуляция дегеніміз не?',
                    'hint': 'Добавление заголовков.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Добавление заголовков к данным на каждом уровне', 'Әр деңгейде деректерге тақырыптарды қосу', True),
                        ('Удаление заголовков', 'Тақырыптарды өшіру', False),
                        ('Сжатие данных', 'Деректерді сығу', False),
                        ('Шифрование данных', 'Деректерді шифрлау', False)
                    ]
                },
                {
                    'text': 'Расположите уровни OSI в правильном порядке (снизу вверх):',
                    'text_kk': 'OSI деңгейлерін дұрыс ретінде салыңыз (төменнен жоғары):',
                    'hint': 'Начните с Физического.',
                    'difficulty': 'Hard',
                    'category': 'Conceptual Analysis',
                    'type': 'sorting',
                    'choices': [
                        ('Физический', 'Физикалық', 1),
                        ('Канальный', 'Арналық', 2),
                        ('Сетевой', 'Желілік', 3),
                        ('Транспортный', 'Көліктік', 4),
                        ('Сессионный', 'Сессиялық', 5),
                        ('Представления', 'Көрсету', 6),
                        ('Прикладной', 'Қолданбалы', 7)
                    ]
                }
            ]
        },
        # Модуль 3: Стек TCP/IP
        {
            'slug': 'tcp_ip',
            'questions': [
                {
                    'text': 'Сколько уровней в модели TCP/IP?',
                    'text_kk': 'TCP/IP моделіне қанша деңгей кіреді?',
                    'hint': 'Обычно 4 уровня.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('3', '3', False),
                        ('4', '4', True),
                        ('5', '5', False),
                        ('7', '7', False)
                    ]
                },
                {
                    'text': 'Какой протокол TCP/IP обеспечивает надежную доставку данных?',
                    'text_kk': 'TCP/IP протоколының қандайсы деректердің сенімді жеткізілуін қамтамасыз етеді?',
                    'hint': 'С установлением соединения.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('UDP', 'UDP', False),
                        ('TCP', 'TCP', True),
                        ('IP', 'IP', False),
                        ('ICMP', 'ICMP', False)
                    ]
                },
                {
                    'text': 'Какой протокол использует датаграммы без подтверждения доставки?',
                    'text_kk': 'Жеткізу растамасыз датаграммаларды қолданатын протокол қандай?',
                    'hint': 'Ненадежный, но быстрый.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('TCP', 'TCP', False),
                        ('UDP', 'UDP', True),
                        ('FTP', 'FTP', False),
                        ('HTTP', 'HTTP', False)
                    ]
                },
                {
                    'text': 'Какой протокол отвечает за маршрутизацию в стеке TCP/IP?',
                    'text_kk': 'TCP/IP стегінде маршрутизацияға қандай протокол жауап береді?',
                    'hint': 'Интернет-протокол.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('TCP', 'TCP', False),
                        ('UDP', 'UDP', False),
                        ('IP', 'IP', True),
                        ('HTTP', 'HTTP', False)
                    ]
                },
                {
                    'text': 'На каком уровне модели TCP/IP работает протокол HTTP?',
                    'text_kk': 'HTTP протоколы TCP/IP моделінің қай деңгейінде жұмыс істейді?',
                    'hint': 'Прикладной уровень.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Транспортный', 'Көліктік', False),
                        ('Интернет', 'Интернет', False),
                        ('Прикладной', 'Қолданбалы', True),
                        ('Сетевой доступ', 'Желілік қатынау', False)
                    ]
                },
                {
                    'text': 'Что такое трехстороннее рукопожатие в TCP?',
                    'text_kk': 'TCP-дегі үш жақты қол басу дегеніміз не?',
                    'hint': 'Установление соединения.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Процесс установки соединения между клиентом и сервером', 'Клиент мен сервер арасындағы байланысты орнату процесі', True),
                        ('Шифрование данных', 'Деректерді шифрлау', False),
                        ('Сжатие данных', 'Деректерді сығу', False),
                        ('Обнаружение ошибок', 'Қателіктерді анықтау', False)
                    ]
                },
                {
                    'text': 'Какой порт по умолчанию использует HTTP?',
                    'text_kk': 'HTTP әдепкілікті қандай портты қолданады?',
                    'hint': '80.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('21', '21', False),
                        ('22', '22', False),
                        ('80', '80', True),
                        ('443', '443', False)
                    ]
                },
                {
                    'text': 'Какой протокол используется для отправки email?',
                    'text_kk': 'Электрондық пошту жіберу үшін қандай протокол қолданылады?',
                    'hint': 'Simple Mail Transfer Protocol.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('FTP', 'FTP', False),
                        ('SMTP', 'SMTP', True),
                        ('POP3', 'POP3', False),
                        ('IMAP', 'IMAP', False)
                    ]
                },
                {
                    'text': 'Что делает протокол DNS?',
                    'text_kk': 'DNS протоколы не істейді?',
                    'hint': 'Переводит имена в адреса.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Переводит доменные имена в IP-адреса', 'Домен аттарын IP-адрестарға аудырып береді', True),
                        ('Отправляет email', 'Электрондық пошту жібереді', False),
                        ('Передаёт файлы', 'Файлдарды береді', False),
                        ('Шифрует данные', 'Деректерді шифрлайды', False)
                    ]
                },
                {
                    'text': 'Сопоставьте протоколы с их функциями:',
                    'text_kk': 'Протоколдарды олардың функцияларымен салыстырыңыз:',
                    'hint': 'Сопоставьте пары.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'matching',
                    'choices': [
                        ('TCP', 'TCP', 'Надежная доставка с подтверждением', 'Растаумен сенімді жеткізу'),
                        ('UDP', 'UDP', 'Быстрая доставка без подтверждения', 'Растаусыз жылдам жеткізу'),
                        ('IP', 'IP', 'Маршрутизация и адресация', 'Маршрутизация және адресация'),
                        ('HTTP', 'HTTP', 'Передача веб-страниц', 'Веб-беттерді беру')
                    ]
                }
            ]
        },
        # Модуль 4: IP-адресация
        {
            'slug': 'ip_addressing',
            'questions': [
                {
                    'text': 'Сколько бит в IPv4-адресе?',
                    'text_kk': 'IPv4-адресінде қанша бит бар?',
                    'hint': '32.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('16', '16', False),
                        ('32', '32', True),
                        ('64', '64', False),
                        ('128', '128', False)
                    ]
                },
                {
                    'text': 'Сколько бит в IPv6-адресе?',
                    'text_kk': 'IPv6-адресінде қанша бит бар?',
                    'hint': '128.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('32', '32', False),
                        ('64', '64', False),
                        ('128', '128', True),
                        ('256', '256', False)
                    ]
                },
                {
                    'text': 'Какой класс IP-адреса предназначен для крупных сетей?',
                    'text_kk': 'Ірі желілер үшін қандай класс IP-адресы арналған?',
                    'hint': 'Класс A.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('A', 'A', True),
                        ('B', 'B', False),
                        ('C', 'C', False),
                        ('D', 'D', False)
                    ]
                },
                {
                    'text': 'Чему равна маска подсети для класса C по умолчанию?',
                    'text_kk': 'C классы үшін әдепкілікті ішкі желі маскасы неге тең?',
                    'hint': '255.255.255.0.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('255.0.0.0', '255.0.0.0', False),
                        ('255.255.0.0', '255.255.0.0', False),
                        ('255.255.255.0', '255.255.255.0', True),
                        ('255.255.255.255', '255.255.255.255', False)
                    ]
                },
                {
                    'text': 'Что такое подсеть?',
                    'text_kk': 'Ішкі желі дегеніміз не?',
                    'hint': 'Разделение большой сети.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Часть большой сети, выделенная для определенной группы устройств', 'Күрделі желінің белгілі бір құрылғылар тобына арналған бөлігі', True),
                        ('Отдельная сеть не связанная с основной', 'Негізгі желімен байланыспайтын бөлек желі', False),
                        ('Тип сетевого оборудования', 'Желілік жабдықтың түрі', False),
                        ('Протокол маршрутизации', 'Маршрутизация протоколы', False)
                    ]
                },
                {
                    'text': 'Какой адрес используется для широковещательной передачи в подсети 192.168.1.0/24?',
                    'text_kk': '192.168.1.0/24 ішкі желісінде кеңінен беру үшін қандай адрес қолданылады?',
                    'hint': 'Последний адрес.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('192.168.1.0', '192.168.1.0', False),
                        ('192.168.1.1', '192.168.1.1', False),
                        ('192.168.1.255', '192.168.1.255', True),
                        ('192.168.1.256', '192.168.1.256', False)
                    ]
                },
                {
                    'text': 'Что такое NAT?',
                    'text_kk': 'NAT дегеніміз не?',
                    'hint': 'Перевод адресов.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Network Address Translation - трансляция сетевых адресов', 'Network Address Translation - желілік адресстерді трансляциялау', True),
                        ('Протокол маршрутизации', 'Маршрутизация протоколы', False),
                        ('Тип сетевого оборудования', 'Желілік жабдықтың түрі', False),
                        ('Система безопасности', 'Қауіпсіздік жүйесі', False)
                    ]
                },
                {
                    'text': 'Какой из адресов является частным (private)?',
                    'text_kk': 'Адресстердің қайсысы жеке (private)?',
                    'hint': '192.168.x.x.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('8.8.8.8', '8.8.8.8', False),
                        ('192.168.1.1', '192.168.1.1', True),
                        ('1.1.1.1', '1.1.1.1', False),
                        ('255.255.255.255', '255.255.255.255', False)
                    ]
                },
                {
                    'text': 'Для чего используется протокол DHCP?',
                    'text_kk': 'DHCP протоколы не үшін қолданылады?',
                    'hint': 'Автоматическое назначение IP.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('Автоматическое назначение IP-адресов устройствам', 'Құрылғыларға IP-адресстерді автоматты түрде тағайындау', True),
                        ('Перевод доменных имен в IP', 'Домен аттарын IP-ге аудару', False),
                        ('Маршрутизация данных', 'Деректерді маршрутизациялау', False),
                        ('Шифрование данных', 'Деректерді шифрлау', False)
                    ]
                },
                {
                    'text': 'Сколько октетов в IPv4-адресе?',
                    'text_kk': 'IPv4-адресінде қанша октет бар?',
                    'hint': '4.',
                    'difficulty': 'Easy',
                    'category': 'Conceptual Analysis',
                    'type': 'multiple_choice',
                    'choices': [
                        ('2', '2', False),
                        ('4', '4', True),
                        ('6', '6', False),
                        ('8', '8', False)
                    ]
                }
            ]
        }
    ]
    
    # Создаем вопросы для каждого модуля
    for module_data in modules_questions:
        module = Module.objects.get(slug=module_data['slug'])
        
        for question_data in module_data['questions']:
            question = Question.objects.create(
                module=module,
                text=question_data['text'],
                text_kk=question_data.get('text_kk', ''),
                hint=question_data.get('hint', ''),
                explanation=question_data.get('explanation', ''),
                difficulty=question_data['difficulty'],
                category=question_data['category'],
                type=question_data['type']
            )
            
            # Создаем варианты ответов
            if question_data['type'] == 'multiple_choice':
                for i, choice_data in enumerate(question_data['choices']):
                    Choice.objects.create(
                        question=question,
                        text=choice_data[0],
                        text_kk=choice_data[1],
                        is_correct=choice_data[2],
                        order=i
                    )
            elif question_data['type'] == 'sorting':
                for i, choice_data in enumerate(question_data['choices']):
                    Choice.objects.create(
                        question=question,
                        text=choice_data[0],
                        text_kk=choice_data[1],
                        order=choice_data[2]
                    )
            elif question_data['type'] == 'matching':
                for i, choice_data in enumerate(question_data['choices']):
                    Choice.objects.create(
                        question=question,
                        text=choice_data[0],
                        text_kk=choice_data[1],
                        pair_text=choice_data[2],
                        pair_text_kk=choice_data[3],
                        order=i
                    )
    
    print("Все вопросы успешно добавлены!")


if __name__ == '__main__':
    run()
