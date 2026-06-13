import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Module, Question, Choice

def run():
    # Создание модулей
    modules_data = [
        {
            'name': 'Введение', 
            'name_kk': 'Кіріспе', 
            'slug': 'introduction', 
            'order': 1, 
            'description': 'Основы сетевых технологий, терминология и история развития сетей.',
            'description_kk': 'Желілік технологиялар негіздері, терминология және желілердің даму тарихы.'
        },
        {
            'name': 'Модель OSI', 
            'name_kk': 'OSI моделі', 
            'slug': 'osi_model', 
            'order': 2, 
            'description': 'Детальный разбор семи уровней взаимодействия сетевых систем.',
            'description_kk': 'Желілік жүйелердің өзара әрекеттесуінің жеті деңгейін егжей-тегжейлі талдау.'
        },
        {
            'name': 'Стек TCP/IP', 
            'name_kk': 'TCP/IP стегі', 
            'slug': 'tcp_ip', 
            'order': 3, 
            'description': 'Протоколы стека TCP/IP, их функции и сравнение с моделью OSI.',
            'description_kk': 'TCP/IP стегінің хаттамалары, олардың функциялары және OSI моделімен салыстыру.'
        },
        {
            'name': 'IP-адресация', 
            'name_kk': 'IP-мекенжайлау', 
            'slug': 'ip_addressing', 
            'order': 4, 
            'description': 'IPv4, IPv6, маски подсетей и основы планирования адресного пространства.',
            'description_kk': 'IPv4, IPv6, ішкі желі маскалары және адрестік кеңістікті жоспарлау негіздері.'
        },
        {
            'name': 'Протоколы', 
            'name_kk': 'Хаттамалар', 
            'slug': 'protocols', 
            'order': 5, 
            'description': 'TCP/UDP, HTTP, DNS, DHCP и другие протоколы прикладного уровня.',
            'description_kk': 'TCP/UDP, HTTP, DNS, DHCP және басқа да қолданбалы деңгейдегі хаттамалар.'
        },
        {
            'name': 'Локальные сети', 
            'name_kk': 'Жергілікті желілер', 
            'slug': 'lan', 
            'order': 6, 
            'description': 'Ethernet, коммутаторы, VLAN и проектирование офисных сетей.',
            'description_kk': 'Ethernet, коммутаторлар, VLAN және кеңсе желілерін жобалау.'
        },
        {
            'name': 'Коммутация', 
            'name_kk': 'Коммутация', 
            'slug': 'switching', 
            'order': 7, 
            'description': 'Принципы работы коммутаторов, таблицы MAC-адресов и STP.',
            'description_kk': 'Коммутаторлардың жұмыс істеу принциптері, MAC-мекенжайлар кестелері және STP.'
        },
        {
            'name': 'Маршрутизация', 
            'name_kk': 'Маршруттау', 
            'slug': 'routing', 
            'order': 8, 
            'description': 'Основы маршрутизации, статические и динамические маршруты, RIP, OSPF.',
            'description_kk': 'Маршруттау негіздері, статикалық және динамикалық маршруттар, RIP, OSPF.'
        },
        {
            'name': 'Безопасность', 
            'name_kk': 'Қауіпсіздік', 
            'slug': 'security', 
            'order': 9, 
            'description': 'Брандмауэры, ACL, шифрование и защита сетевой инфраструктуры.',
            'description_kk': 'Брандмауэрлер, ACL, шифрлау және желілік инфрақұрылымды қорғау.'
        },
        {
            'name': 'Беспроводные сети', 
            'name_kk': 'Сымсыз желілер', 
            'slug': 'wireless', 
            'order': 10, 
            'description': 'Wi-Fi, Bluetooth, стандарты 802.11 и безопасность WLAN.',
            'description_kk': 'Wi-Fi, Bluetooth, 802.11 стандарттары және WLAN қауіпсіздігі.'
        },
        {
            'name': 'Облачные технологии', 
            'name_kk': 'Бұлтты технологиялар', 
            'slug': 'cloud', 
            'order': 11, 
            'description': 'Облачные вычисления, модели SaaS, PaaS, IaaS и виртуализация.',
            'description_kk': 'Бұлтты есептеулер, SaaS, PaaS, IaaS модельдері және виртуалдау.'
        },
        {
            'name': 'Клиент-сервер', 
            'name_kk': 'Клиент-сервер', 
            'slug': 'client_server', 
            'order': 12, 
            'description': 'Архитектура распределенных систем и работа серверных служб.',
            'description_kk': 'Үлестірілген жүйелердің архитектурасы және серверлік қызметтердің жұмысы.'
        },
        {
            'name': 'Итоговый проект', 
            'name_kk': 'Қорытынды жоба', 
            'slug': 'final_project', 
            'order': 13, 
            'description': 'Развертывание виртуальной лаборатории и проектирование сети предприятия.',
            'description_kk': 'Виртуалды зертхананы өрістету және кәсіпорын желісін жобалау.'
        },
    ]

    for data in modules_data:
        module, created = Module.objects.get_or_create(slug=data['slug'], defaults=data)
        if not created:
            module.name = data['name']
            module.name_kk = data['name_kk']
            module.order = data['order']
            module.description = data['description']
            module.description_kk = data['description_kk']
            module.save()

    # Добавление вопросов для Модели OSI (как пример)
    osi_module = Module.objects.get(slug='osi_model')
    q1, _ = Question.objects.get_or_create(
        module=osi_module,
        text='Какой уровень модели OSI отвечает за логическую адресацию и маршрутизацию в сети?',
        defaults={
            'text_kk': 'OSI моделінің қай деңгейі желідегі логикалық адрестеу мен маршруттауға жауап береді?',
            'hint': 'Подумайте об IP-адресах и маршрутизаторах.', 
            'difficulty': 'Intermediate', 
            'category': 'Conceptual Analysis'
        }
    )
    if not _: # Если вопрос уже был, обновим казахский текст
        q1.text_kk = 'OSI моделінің қай деңгейі желідегі логикалық адрестеу мен маршруттауға жауап береді?'
        q1.save()

    Choice.objects.get_or_create(question=q1, text='Канальный уровень (Data Link)', defaults={'text_kk': 'Арналық деңгей (Data Link)', 'is_correct': False})
    Choice.objects.get_or_create(question=q1, text='Сетевой уровень (Network)', defaults={'text_kk': 'Желілік деңгей (Network)', 'is_correct': True})
    Choice.objects.get_or_create(question=q1, text='Транспортный уровень (Transport)', defaults={'text_kk': 'Көліктік деңгей (Transport)', 'is_correct': False})
    Choice.objects.get_or_create(question=q1, text='Физический уровень (Physical)', defaults={'text_kk': 'Физикалық деңгей (Physical)', 'is_correct': False})

    # Обновим казахские тексты для Choice, если они уже были
    for choice in Choice.objects.filter(question=q1):
        if choice.text == 'Канальный уровень (Data Link)': choice.text_kk = 'Арналық деңгей (Data Link)'
        elif choice.text == 'Сетевой уровень (Network)': choice.text_kk = 'Желілік деңгей (Network)'
        elif choice.text == 'Транспортный уровень (Transport)': choice.text_kk = 'Көліктік деңгей (Transport)'
        elif choice.text == 'Физический уровень (Physical)': choice.text_kk = 'Физикалық деңгей (Physical)'
        choice.save()

    # Добавление вопросов для Введения (чтобы можно было начать)
    intro_module = Module.objects.get(slug='introduction')
    q2, _ = Question.objects.get_or_create(
        module=intro_module,
        text='Что такое компьютерная сеть?',
        defaults={
            'text_kk': 'Компьютерлік желі дегеніміз не?',
            'hint': 'Базовое определение.', 
            'difficulty': 'Easy', 
            'category': 'Basics'
        }
    )
    if not _:
        q2.text_kk = 'Компьютерлік желі дегеніміз не?'
        q2.save()

    Choice.objects.get_or_create(question=q2, text='Группа соединенных компьютеров для обмена данными', defaults={'text_kk': 'Деректермен алмасу үшін қосылған компьютерлер тобы', 'is_correct': True})
    Choice.objects.get_or_create(question=q2, text='Один мощный компьютер', defaults={'text_kk': 'Бір қуатты компьютер', 'is_correct': False})
    Choice.objects.get_or_create(question=q2, text='Программа для чата', defaults={'text_kk': 'Чатқа арналған бағдарлама', 'is_correct': False})

    for choice in Choice.objects.filter(question=q2):
        if choice.text == 'Группа соединенных компьютеров для обмена данными': choice.text_kk = 'Деректермен алмасу үшін қосылған компьютерлер тобы'
        elif choice.text == 'Один мощный компьютер': choice.text_kk = 'Бір қуатты компьютер'
        elif choice.text == 'Программа для чата': choice.text_kk = 'Чатқа арналған бағдарлама'
        choice.save()

    # Обновим лабораторные работы
    from laboratory.models import Lab
    lab_hostname, _ = Lab.objects.get_or_create(
        module=intro_module,
        defaults={
            'title': 'Настройка Hostname',
            'title_kk': 'Hostname баптау',
            'description': 'Для изменения имени устройства используется команда <i>hostname ИМЯ</i> в режиме глобальной конфигурации.',
            'description_kk': 'Құрылғының атын өзгерту үшін жаһандық конфигурация режимінде <i>hostname АТЫ</i> командасы қолданылады.',
            'scenario_data': {}
        }
    )
    if not _:
        lab_hostname.title_kk = 'Hostname баптау'
        lab_hostname.description_kk = 'Құрылғының атын өзгерту үшін жаһандық конфигурация режимінде <i>hostname АТЫ</i> командасы қолданылады.'
        lab_hostname.save()

    print("База данных успешно инициализирована модулями, лабораторными работами и тестовыми вопросами (RU/KK).")

if __name__ == '__main__':
    run()
