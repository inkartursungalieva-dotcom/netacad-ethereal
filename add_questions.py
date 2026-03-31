import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Module, Question, Choice

def add_question(module_slug, text, choices, hint='', difficulty='Intermediate', category='Conceptual Analysis'):
    try:
        module = Module.objects.get(slug=module_slug)
        question, created = Question.objects.get_or_create(
            module=module,
            text=text,
            defaults={'hint': hint, 'difficulty': difficulty, 'category': category}
        )
        if created:
            for choice_text, is_correct in choices:
                Choice.objects.get_or_create(question=question, text=choice_text, defaults={'is_correct': is_correct})
            return True
        return False
    except Module.DoesNotExist:
        print(f"Module {module_slug} not found.")
        return False

def run():
    # Cleanup
    Module.objects.filter(slug='9').delete()
    Question.objects.all().delete() # Clear all to ensure exactly 20 each
    
    # 1. Введение (introduction) - 20 вопросов
    intro_questions = [
        ("Что такое компьютерная сеть?", [("Группа соединенных компьютеров для обмена данными", True), ("Один мощный компьютер", False), ("Программа для чата", False), ("Жесткий диск", False)], "Базовое определение.", "Easy", "Conceptual Analysis"),
        ("Какова основная цель компьютерной сети?", [("Совместное использование ресурсов", True), ("Увеличение веса компьютера", False), ("Замедление работы интернета", False), ("Защита от пыли", False)], "Зачем мы их соединяем?", "Easy", "Conceptual Analysis"),
        ("Что такое топология сети?", [("Физическое или логическое расположение узлов", True), ("Цвет сетевых кабелей", False), ("Скорость интернета", False), ("Тип операционной системы", False)], "Схема соединений.", "Intermediate", "Conceptual Analysis"),
        ("Какая топология использует центральное устройство (коммутатор)?", [("Звезда (Star)", True), ("Шина (Bus)", False), ("Кольцо (Ring)", False), ("Ячеистая (Mesh)", False)], "Центральный узел.", "Intermediate", "Conceptual Analysis"),
        ("Что такое LAN?", [("Локальная вычислительная сеть", True), ("Глобальная сеть", False), ("Спутниковая связь", False), ("Тип кабеля", False)], "Масштаб сети.", "Easy", "Conceptual Analysis"),
        ("Что такое WAN?", [("Глобальная вычислительная сеть", True), ("Локальная сеть", False), ("Домашняя сеть", False), ("Беспроводная сеть", False)], "Сеть на больших расстояниях.", "Easy", "Conceptual Analysis"),
        ("Какой кабель чаще всего используется в современных LAN?", [("Витая пара (UTP/STP)", True), ("Коаксиальный", False), ("Телефонный", False), ("Силовой", False)], "Стандарт соединений.", "Easy", "Conceptual Analysis"),
        ("Что такое пропускная способность (Bandwidth)?", [("Максимальная скорость передачи данных", True), ("Длина кабеля", False), ("Количество компьютеров в сети", False), ("Вес данных", False)], "Характеристика канала.", "Intermediate", "Conceptual Analysis"),
        ("Что такое задержка (Latency)?", [("Время, необходимое для прохождения данных", True), ("Скорость скачивания", False), ("Размер файла", False), ("Тип разъема", False)], "Временной параметр.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол является основой интернета?", [("TCP/IP", True), ("HTTP", False), ("FTP", False), ("SMTP", False)], "Стек протоколов.", "Easy", "Conceptual Analysis"),
        ("Что такое узел (Node) в сети?", [("Любое устройство, подключенное к сети", True), ("Только сервер", False), ("Только кабель", False), ("Программная ошибка", False)], "Сетевое устройство.", "Easy", "Conceptual Analysis"),
        ("Что такое сервер?", [("Компьютер, предоставляющий услуги другим", True), ("Компьютер, который только играет в игры", False), ("Принтер", False), ("Клавиатура", False)], "Роль в сети.", "Easy", "Conceptual Analysis"),
        ("Что такое клиент?", [("Устройство, запрашивающее услуги у сервера", True), ("Тот, кто покупает компьютер", False), ("Сетевой кабель", False), ("Тип вируса", False)], "Роль в сети.", "Easy", "Conceptual Analysis"),
        ("Какая топология самая надежная (каждый с каждым)?", [("Ячеистая (Mesh)", True), ("Звезда", False), ("Шина", False), ("Кольцо", False)], "Максимальная связность.", "Hard", "Conceptual Analysis"),
        ("Что такое пакет (Packet)?", [("Единица данных, передаваемая по сети", True), ("Программа для архивации", False), ("Сумка для ноутбука", False), ("Тип монитора", False)], "Передача данных.", "Intermediate", "Conceptual Analysis"),
        ("Что такое протокол?", [("Набор правил взаимодействия", True), ("Список компьютеров", False), ("Сетевой пароль", False), ("Имя администратора", False)], "Правила общения.", "Easy", "Conceptual Analysis"),
        ("Что такое Peer-to-Peer (P2P) сеть?", [("Сеть без выделенного сервера", True), ("Сеть только для печати", False), ("Сеть со сверхмощным сервером", False), ("Спутниковая сеть", False)], "Равноправная сеть.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Intranet?", [("Частная сеть организации", True), ("Глобальный интернет", False), ("Сайт для покупок", False), ("Тип модема", False)], "Внутренняя сеть.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Extranet?", [("Часть интранета, доступная партнерам", True), ("Внешний жесткий диск", False), ("Космическая связь", False), ("Бесплатный Wi-Fi", False)], "Расширенная внутренняя сеть.", "Intermediate", "Conceptual Analysis"),
        ("Какое устройство соединяет разные сети?", [("Маршрутизатор (Router)", True), ("Клавиатура", False), ("Монитор", False), ("Мышь", False)], "Межсетевое устройство.", "Easy", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in intro_questions:
        add_question('introduction', text, choices, hint, diff, cat)

    # 2. Модель OSI (osi_model) - 20 вопросов
    osi_questions = [
        ("Сколько уровней в модели OSI?", [("7", True), ("5", False), ("4", False), ("8", False)], "Стандарт ISO.", "Easy", "Conceptual Analysis"),
        ("На каком уровне работают IP-адреса?", [("Сетевой (Network)", True), ("Канальный", False), ("Транспортный", False), ("Физический", False)], "Логическая адресация.", "Intermediate", "Conceptual Analysis"),
        ("На каком уровне работают MAC-адреса?", [("Канальный (Data Link)", True), ("Физический", False), ("Сетевой", False), ("Транспортный", False)], "Физическая адресация.", "Intermediate", "Conceptual Analysis"),
        ("Какой уровень отвечает за надежную доставку (TCP)?", [("Транспортный (Transport)", True), ("Сетевой", False), ("Сеансовый", False), ("Прикладной", False)], "Контроль ошибок и потока.", "Intermediate", "Conceptual Analysis"),
        ("На каком уровне работает HTTP?", [("Прикладной (Application)", True), ("Представительский", False), ("Транспортный", False), ("Сетевой", False)], "Взаимодействие с пользователем.", "Easy", "Conceptual Analysis"),
        ("Какой уровень отвечает за шифрование и сжатие данных?", [("Представительский (Presentation)", True), ("Прикладной", False), ("Сеансовый", False), ("Транспортный", False)], "Формат данных.", "Intermediate", "Conceptual Analysis"),
        ("На каком уровне работают кабели и сигналы?", [("Физический (Physical)", True), ("Канальный", False), ("Сетевой", False), ("Транспортный", False)], "Среда передачи.", "Easy", "Conceptual Analysis"),
        ("Какой уровень управляет диалогом между приложениями?", [("Сеансовый (Session)", True), ("Транспортный", False), ("Представительский", False), ("Прикладной", False)], "Поддержание сессии.", "Intermediate", "Conceptual Analysis"),
        ("Как называется единица данных на сетевом уровне?", [("Пакет (Packet)", True), ("Фрейм (Frame)", False), ("Сегмент (Segment)", False), ("Бит (Bit)", False)], "PDU сетевого уровня.", "Intermediate", "Conceptual Analysis"),
        ("Как называется единица данных на канальном уровне?", [("Фрейм (Frame)", True), ("Пакет", False), ("Сегмент", False), ("Дейтаграмма", False)], "PDU канального уровня.", "Intermediate", "Conceptual Analysis"),
        ("Как называется единица данных на транспортном уровне (TCP)?", [("Сегмент (Segment)", True), ("Пакет", False), ("Фрейм", False), ("Бит", False)], "PDU транспортного уровня.", "Intermediate", "Conceptual Analysis"),
        ("На каком уровне работает коммутатор (L2 Switch)?", [("Канальный (Data Link)", True), ("Сетевой", False), ("Физический", False), ("Транспортный", False)], "Работа с MAC-адресами.", "Intermediate", "Conceptual Analysis"),
        ("На каком уровне работает маршрутизатор?", [("Сетевой (Network)", True), ("Транспортный", False), ("Канальный", False), ("Прикладной", False)], "Маршрутизация пакетов.", "Intermediate", "Conceptual Analysis"),
        ("Какой уровень является самым нижним?", [("Физический (Physical)", True), ("Канальный", False), ("Сетевой", False), ("Прикладной", False)], "Начало модели.", "Easy", "Conceptual Analysis"),
        ("Какой уровень является самым верхним?", [("Прикладной (Application)", True), ("Физический", False), ("Транспортный", False), ("Сеансовый", False)], "Конец модели.", "Easy", "Conceptual Analysis"),
        ("Что такое инкапсуляция?", [("Процесс добавления заголовков при движении вниз", True), ("Процесс удаления заголовков", False), ("Тип кабеля", False), ("Вид вируса", False)], "Движение данных сверху вниз.", "Intermediate", "Conceptual Analysis"),
        ("Что такое деинкапсуляция?", [("Процесс удаления заголовков при движении вверх", True), ("Добавление заголовков", False), ("Шифрование", False), ("Сжатие", False)], "Движение данных снизу вверх.", "Intermediate", "Conceptual Analysis"),
        ("На каком уровне работает концентратор (Hub)?", [("Физический (Physical)", True), ("Канальный", False), ("Сетевой", False), ("Транспортный", False)], "Простое повторение сигналов.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол работает на 4 уровне (транспортном) и не гарантирует доставку?", [("UDP", True), ("TCP", False), ("IP", False), ("ICMP", False)], "Быстрый, но ненадежный.", "Intermediate", "Conceptual Analysis"),
        ("Какой уровень отвечает за выбор кратчайшего пути?", [("Сетевой (Network)", True), ("Транспортный", False), ("Канальный", False), ("Физический", False)], "Логика маршрутизации.", "Intermediate", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in osi_questions:
        add_question('osi_model', text, choices, hint, diff, cat)

    # 3. Стек TCP/IP (tcp_ip) - 20 вопросов
    tcp_ip_questions = [
        ("Сколько уровней в классической модели TCP/IP?", [("4", True), ("7", False), ("5", False), ("6", False)], "Стандартная модель DOD.", "Easy", "Conceptual Analysis"),
        ("Какой уровень TCP/IP соответствует сетевому уровню OSI?", [("Межсетевой (Internet)", True), ("Транспортный", False), ("Сетевой доступ", False), ("Прикладной", False)], "IP работает здесь.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол обеспечивает надежную доставку в TCP/IP?", [("TCP", True), ("UDP", False), ("IP", False), ("ICMP", False)], "Установка соединения.", "Easy", "Conceptual Analysis"),
        ("Какой протокол используется для передачи почты?", [("SMTP", True), ("FTP", False), ("HTTP", False), ("DNS", False)], "Почтовый стандарт.", "Easy", "Conceptual Analysis"),
        ("На каком уровне TCP/IP работает протокол IP?", [("Межсетевой (Internet)", True), ("Прикладной", False), ("Транспортный", False), ("Сетевой доступ", False)], "Сердце стека.", "Easy", "Conceptual Analysis"),
        ("Какой протокол разрешает IP-адреса в MAC-адреса?", [("ARP", True), ("RARP", False), ("DHCP", False), ("DNS", False)], "Адресное разрешение.", "Intermediate", "Conceptual Analysis"),
        ("Что такое трехстороннее рукопожатие (Three-way Handshake)?", [("Процесс установления TCP соединения", True), ("Смена пароля", False), ("Тип шифрования", False), ("Завершение сессии", False)], "SYN-SYN/ACK-ACK.", "Intermediate", "Conceptual Analysis"),
        ("Какой уровень TCP/IP объединяет 5, 6 и 7 уровни OSI?", [("Прикладной (Application)", True), ("Транспортный", False), ("Межсетевой", False), ("Сетевой доступ", False)], "Верхние уровни.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол используется для автоматической настройки IP?", [("DHCP", True), ("DNS", False), ("HTTP", False), ("FTP", False)], "Динамическая настройка.", "Easy", "Conceptual Analysis"),
        ("Какой протокол переводит доменные имена в IP-адреса?", [("DNS", True), ("DHCP", False), ("ARP", False), ("ICMP", False)], "Служба имен.", "Easy", "Conceptual Analysis"),
        ("Что такое порт (Port) в TCP/IP?", [("Числовой идентификатор приложения", True), ("Физический разъем", False), ("Тип кабеля", False), ("Сетевой адрес", False)], "Адресация процессов.", "Intermediate", "Conceptual Analysis"),
        ("Какой диапазон портов у HTTP?", [("80", True), ("443", False), ("21", False), ("25", False)], "Стандартный порт веба.", "Easy", "Conceptual Analysis"),
        ("Какой порт использует HTTPS?", [("443", True), ("80", False), ("22", False), ("53", False)], "Безопасный веб.", "Easy", "Conceptual Analysis"),
        ("Какой протокол используется для передачи файлов?", [("FTP", True), ("HTTP", False), ("SMTP", False), ("DNS", False)], "File Transfer.", "Easy", "Conceptual Analysis"),
        ("Что такое ICMP?", [("Протокол управляющих сообщений", True), ("Протокол почты", False), ("Протокол веба", False), ("Протокол маршрутизации", False)], "Используется командой ping.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол работает быстрее: TCP или UDP?", [("UDP", True), ("TCP", False), ("Оба одинаковы", False), ("Зависит от кабеля", False)], "Отсутствие подтверждений.", "Intermediate", "Conceptual Analysis"),
        ("Что такое сокет (Socket)?", [("Комбинация IP-адреса и номера порта", True), ("Сетевая розетка", False), ("Процессорный разъем", False), ("Тип вилки", False)], "Конечная точка соединения.", "Hard", "Conceptual Analysis"),
        ("На каком уровне TCP/IP работает Ethernet?", [("Сетевой доступ (Network Access)", True), ("Межсетевой", False), ("Транспортный", False), ("Прикладной", False)], "Нижний уровень.", "Intermediate", "Conceptual Analysis"),
        ("Какое поле в заголовке IP ограничивает время жизни пакета?", [("TTL (Time To Live)", True), ("Version", False), ("Protocol", False), ("Checksum", False)], "Предотвращение петель.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол используется для удаленного управления (безопасно)?", [("SSH", True), ("Telnet", False), ("HTTP", False), ("FTP", False)], "Замена Telnet.", "Easy", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in tcp_ip_questions:
        add_question('tcp_ip', text, choices, hint, diff, cat)

    # 4. IP-адресация (ip_addressing) - 20 вопросов
    ip_questions = [
        ("Сколько бит в адресе IPv4?", [("32", True), ("64", False), ("128", False), ("48", False)], "Четыре октета.", "Easy", "Conceptual Analysis"),
        ("Сколько бит в адресе IPv6?", [("128", True), ("64", False), ("32", False), ("48", False)], "Восемь групп по 16 бит.", "Easy", "Conceptual Analysis"),
        ("К какому классу относится адрес 192.168.1.1?", [("C", True), ("A", False), ("B", False), ("D", False)], "Диапазоны классов.", "Intermediate", "Conceptual Analysis"),
        ("Какая маска подсети по умолчанию для класса C?", [("255.255.255.0", True), ("255.255.0.0", False), ("255.0.0.0", False), ("255.255.255.255", False)], "Префикс /24.", "Easy", "Conceptual Analysis"),
        ("Что такое CIDR?", [("Бесклассовая междоменная маршрутизация", True), ("Тип кабеля", False), ("Модель роутера", False), ("Сетевой протокол", False)], "Запись вида /24.", "Intermediate", "Conceptual Analysis"),
        ("Сколько хостов доступно в подсети /24?", [("254", True), ("256", False), ("128", False), ("1024", False)], "Минус адрес сети и бродкаст.", "Intermediate", "Conceptual Analysis"),
        ("Для чего используется маска подсети?", [("Разделение адреса на сеть и хост", True), ("Шифрование данных", False), ("Увеличение скорости", False), ("Защита от вирусов", False)], "Логическое деление.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Loopback адрес IPv4?", [("127.0.0.1", True), ("192.168.0.1", False), ("10.0.0.1", False), ("0.0.0.0", False)], "Тестирование стека.", "Easy", "Conceptual Analysis"),
        ("Что такое частные (Private) IP-адреса?", [("Адреса для внутренних сетей", True), ("Адреса, которые нельзя купить", False), ("Секретные пароли", False), ("Адреса только для NASA", False)], "RFC 1918.", "Intermediate", "Conceptual Analysis"),
        ("Какое устройство выполняет NAT?", [("Маршрутизатор", True), ("Коммутатор", False), ("Концентратор", False), ("Принтер", False)], "Преобразование адресов.", "Intermediate", "Conceptual Analysis"),
        ("Что такое APIPA (адрес 169.254.x.x)?", [("Автоматический частный IP адрес", True), ("Тип вируса", False), ("Ошибка в Windows", False), ("Протокол маршрутизации", False)], "Когда DHCP недоступен.", "Intermediate", "Conceptual Analysis"),
        ("Как записывается адрес IPv6?", [("Шестнадцатеричными числами", True), ("Десятичными через точку", False), ("Двоичными", False), ("Римскими цифрами", False)], "8 групп через двоеточие.", "Easy", "Conceptual Analysis"),
        ("Что такое широковещательный (Broadcast) адрес?", [("Адрес для всех узлов сети", True), ("Адрес только сервера", False), ("Адрес роутера", False), ("Тип рекламы", False)], "Все единицы в хосте.", "Intermediate", "Conceptual Analysis"),
        ("Какая маска соответствует префиксу /26?", [("255.255.255.192", True), ("255.255.255.128", False), ("255.255.255.224", False), ("255.255.255.240", False)], "Биты маски.", "Hard", "Conceptual Analysis"),
        ("Что такое шлюз по умолчанию (Default Gateway)?", [("IP адрес роутера в локальной сети", True), ("Выход из здания", False), ("Тип кабеля", False), ("Имя администратора", False)], "Выход во внешнюю сеть.", "Easy", "Conceptual Analysis"),
        ("Сколько октетов в адресе IPv4?", [("4", True), ("6", False), ("8", False), ("32", False)], "Разбиение адреса.", "Easy", "Conceptual Analysis"),
        ("Что такое мультикаст (Multicast)?", [("Рассылка группе узлов", True), ("Рассылка всем", False), ("Рассылка одному", False), ("Тип радио", False)], "Групповая передача.", "Intermediate", "Conceptual Analysis"),
        ("Что такое юникаст (Unicast)?", [("Передача одному конкретному узлу", True), ("Передача всем", False), ("Передача группе", False), ("Передача через спутник", False)], "Один на один.", "Easy", "Conceptual Analysis"),
        ("Можно ли использовать адрес сети для хоста?", [("Нет", True), ("Да", False), ("Только по воскресеньям", False), ("Только в IPv6", False)], "Первый адрес диапазона.", "Intermediate", "Conceptual Analysis"),
        ("Какой адрес IPv6 аналогичен 127.0.0.1?", [("::1", True), ("ff02::1", False), ("fe80::1", False), ("2001::1", False)], "Loopback в IPv6.", "Hard", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in ip_questions:
        add_question('ip_addressing', text, choices, hint, diff, cat)

    # 5. Протоколы (protocols) - 20 вопросов
    protocol_questions = [
        ("Что такое HTTP?", [("Протокол передачи гипертекста", True), ("Протокол передачи файлов", False), ("Протокол почты", False), ("Тип кабеля", False)], "Основа веба.", "Easy", "Conceptual Analysis"),
        ("Какой протокол используется для защищенного просмотра веб-страниц?", [("HTTPS", True), ("HTTP", False), ("FTP", False), ("Telnet", False)], "S означает Secure.", "Easy", "Conceptual Analysis"),
        ("Для чего используется протокол DHCP?", [("Автоматическое назначение IP-адресов", True), ("Перевод имен в IP", False), ("Передача файлов", False), ("Удаленное управление", False)], "Dynamic Host Configuration.", "Easy", "Conceptual Analysis"),
        ("Какой протокол используется для синхронизации времени?", [("NTP", True), ("DNS", False), ("SNMP", False), ("HTTP", False)], "Network Time Protocol.", "Intermediate", "Conceptual Analysis"),
        ("Для чего нужен протокол SNMP?", [("Мониторинг и управление сетевыми устройствами", True), ("Просмотр веб-сайтов", False), ("Отправка почты", False), ("Чат", False)], "Simple Network Management.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол используется для передачи файлов через терминал?", [("TFTP", True), ("HTTP", False), ("SMTP", False), ("ICMP", False)], "Trivial FTP.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Telnet?", [("Протокол для удаленного управления (незащищенный)", True), ("Тип телевизора", False), ("Сетевой кабель", False), ("Браузер", False)], "Старый стандарт.", "Easy", "Conceptual Analysis"),
        ("Какой протокол используется для получения почты (скачивание с сервера)?", [("POP3", True), ("SMTP", False), ("FTP", False), ("HTTP", False)], "Post Office Protocol.", "Easy", "Conceptual Analysis"),
        ("Какой протокол позволяет работать с почтой прямо на сервере?", [("IMAP", True), ("POP3", False), ("SMTP", False), ("DNS", False)], "Interactive Mail Access.", "Intermediate", "Conceptual Analysis"),
        ("Что такое LDAP?", [("Протокол доступа к каталогам", True), ("Тип диска", False), ("Сетевая игра", False), ("Протокол времени", False)], "Lightweight Directory Access.", "Hard", "Conceptual Analysis"),
        ("Какой протокол используется для передачи потокового видео?", [("RTP", True), ("HTTP", False), ("TCP", False), ("FTP", False)], "Real-time Transport.", "Intermediate", "Conceptual Analysis"),
        ("Для чего используется протокол SSH?", [("Безопасный удаленный доступ", True), ("Простая передача файлов", False), ("Просмотр видео", False), ("Печать документов", False)], "Secure Shell.", "Easy", "Conceptual Analysis"),
        ("Что такое SIP?", [("Протокол для установления сессий (VoIP)", True), ("Тип напитка", False), ("Протокол почты", False), ("Сетевая карта", False)], "Session Initiation.", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол используется для обмена сообщениями об ошибках в сети?", [("ICMP", True), ("TCP", False), ("UDP", False), ("IP", False)], "Internet Control Message.", "Intermediate", "Conceptual Analysis"),
        ("Что такое протокол ARP?", [("Разрешение IP в MAC", True), ("Разрешение MAC в IP", False), ("Маршрутизация", False), ("Шифрование", False)], "Address Resolution.", "Intermediate", "Conceptual Analysis"),
        ("Для чего нужен протокол NAT?", [("Преобразование частных адресов в публичные", True), ("Сжатие данных", False), ("Проверка вирусов", False), ("Синхронизация времени", False)], "Network Address Translation.", "Intermediate", "Conceptual Analysis"),
        ("Что такое протокол IGMP?", [("Управление группами мультикаста", True), ("Протокол почты", False), ("Протокол веба", False), ("Тип кабеля", False)], "Internet Group Management.", "Hard", "Conceptual Analysis"),
        ("Какой протокол используется для передачи гипертекста через TLS?", [("HTTPS", True), ("HTTP", False), ("FTP", False), ("SSH", False)], "Порт 443.", "Easy", "Conceptual Analysis"),
        ("Что такое протокол BGP?", [("Протокол граничного шлюза (интернет-маршрутизация)", True), ("Тип игры", False), ("Протокол почты", False), ("Локальный протокол", False)], "Border Gateway Protocol.", "Hard", "Conceptual Analysis"),
        ("Какой протокол используется для автоматической настройки IPv6 узлов?", [("SLAAC", True), ("DHCP", False), ("ARP", False), ("DNS", False)], "Stateless Address Autoconfiguration.", "Hard", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in protocol_questions:
        add_question('protocols', text, choices, hint, diff, cat)

    # 6. Локальные сети (lan) - 20 вопросов
    lan_questions = [
        ("Что такое Ethernet?", [("Семейство технологий пакетной передачи данных для LAN", True), ("Марка роутера", False), ("Название интернета", False), ("Тип процессора", False)], "Стандарт IEEE 802.3.", "Easy", "Conceptual Analysis"),
        ("Какое устройство используется для создания LAN в топологии 'звезда'?", [("Коммутатор (Switch)", True), ("Модем", False), ("Принтер", False), ("Сканер", False)], "Центральный узел.", "Easy", "Conceptual Analysis"),
        ("Что такое VLAN?", [("Виртуальная локальная сеть", True), ("Очень большая сеть", False), ("Тип кабеля", False), ("Вид вируса", False)], "Virtual LAN.", "Intermediate", "Conceptual Analysis"),
        ("Какой стандарт описывает Wi-Fi?", [("IEEE 802.11", True), ("IEEE 802.3", False), ("IEEE 802.5", False), ("IEEE 802.1", False)], "Беспроводные LAN.", "Easy", "Conceptual Analysis"),
        ("Что такое MAC-адрес?", [("Уникальный физический адрес устройства", True), ("Адрес компьютера Apple", False), ("Имя пользователя", False), ("Пароль от Wi-Fi", False)], "Media Access Control.", "Easy", "Conceptual Analysis"),
        ("Какой кабель поддерживает скорость до 10 Гбит/с в LAN?", [("Витая пара Cat 6a/7", True), ("Телефонный провод", False), ("Коаксиальный", False), ("Силовой", False)], "Категории кабеля.", "Intermediate", "Conceptual Analysis"),
        ("Что такое коллизия (Collision)?", [("Одновременная передача данных двумя узлами", True), ("Тип разъема", False), ("Сетевой протокол", False), ("Настройка роутера", False)], "Проблема в полудуплексных сетях.", "Intermediate", "Conceptual Analysis"),
        ("Что такое полнодуплексный (Full-Duplex) режим?", [("Одновременная передача и прием", True), ("Только передача", False), ("Только прием", False), ("Передача по очереди", False)], "Эффективная работа.", "Intermediate", "Conceptual Analysis"),
        ("Какое устройство разделяет домены коллизий?", [("Коммутатор (Switch)", True), ("Концентратор (Hub)", False), ("Репитер", False), ("Кабель", False)], "Умное устройство L2.", "Intermediate", "Conceptual Analysis"),
        ("Для чего используется протокол STP?", [("Предотвращение петель в сети", True), ("Увеличение скорости", False), ("Шифрование Wi-Fi", False), ("Раздача IP", False)], "Spanning Tree Protocol.", "Hard", "Conceptual Analysis"),
        ("Что такое транк (Trunk) порт?", [("Порт, передающий трафик нескольких VLAN", True), ("Порт для зарядки", False), ("Сломанный порт", False), ("Порт только для сервера", False)], "Соединение коммутаторов.", "Hard", "Conceptual Analysis"),
        ("Какой разъем используется для кабеля 'витая пара'?", [("RJ-45", True), ("USB", False), ("HDMI", False), ("BNC", False)], "Стандартный коннектор.", "Easy", "Conceptual Analysis"),
        ("Что такое Power over Ethernet (PoE)?", [("Питание устройств через сетевой кабель", True), ("Очень быстрый интернет", False), ("Тип розетки", False), ("Вид батарейки", False)], "Питание камер и IP-телефонов.", "Intermediate", "Conceptual Analysis"),
        ("Какова максимальная длина сегмента витой пары без репитера?", [("100 метров", True), ("500 метров", False), ("1 км", False), ("10 метров", False)], "Ограничение стандарта.", "Easy", "Conceptual Analysis"),
        ("Что такое широковещательный шторм (Broadcast Storm)?", [("Избыточный трафик, парализующий сеть", True), ("Гроза с молниями", False), ("Тип вируса", False), ("Быстрое скачивание", False)], "Результат петель в L2.", "Intermediate", "Conceptual Analysis"),
        ("Какое устройство работает на 2 уровне модели OSI?", [("Коммутатор", True), ("Маршрутизатор", False), ("Концентратор", False), ("Сервер", False)], "L2 устройства.", "Easy", "Conceptual Analysis"),
        ("Что такое домен широковещания (Broadcast Domain)?", [("Группа устройств, получающих бродкаст друг друга", True), ("Сайт в интернете", False), ("Имя компьютера", False), ("Тип кабеля", False)], "Логический сегмент сети.", "Intermediate", "Conceptual Analysis"),
        ("Для чего используется стандарт 802.1Q?", [("Тэггирование трафика VLAN", True), ("Шифрование", False), ("Сжатие", False), ("Маршрутизация", False)], "Dot1q.", "Hard", "Conceptual Analysis"),
        ("Что такое WLAN?", [("Беспроводная локальная сеть", True), ("Глобальная сеть", False), ("Проводная сеть", False), ("Спутниковая сеть", False)], "Wireless LAN.", "Easy", "Conceptual Analysis"),
        ("Какое преимущество у оптоволокна перед медью?", [("Большее расстояние и отсутствие помех", True), ("Низкая цена", False), ("Легкость в установке", False), ("Можно завязывать узлом", False)], "Оптическая связь.", "Intermediate", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in lan_questions:
        add_question('lan', text, choices, hint, diff, cat)

    # 7. Коммутация (switching) - 20 вопросов
    switching_questions = [
        ("Как коммутатор узнает, куда отправить фрейм?", [("Изучает MAC-адреса отправителей", True), ("Спрашивает у роутера", False), ("Рассылает всем всегда", False), ("Использует IP-адреса", False)], "Таблица MAC-адресов.", "Intermediate", "Conceptual Analysis"),
        ("Что делает коммутатор, если адреса назначения нет в его таблице?", [("Рассылает фрейм во все порты (Flooding)", True), ("Удаляет фрейм", False), ("Ждет 5 минут", False), ("Выключается", False)], "Unknown Unicast Flooding.", "Intermediate", "Conceptual Analysis"),
        ("Какая таблица используется коммутатором для пересылки?", [("MAC-table (или CAM)", True), ("Routing table", False), ("ARP table", False), ("DNS cache", False)], "Content Addressable Memory.", "Intermediate", "Conceptual Analysis"),
        ("В чем отличие коммутатора от концентратора (Hub)?", [("Коммутатор отправляет данные адресату, а не всем", True), ("Коммутатор медленнее", False), ("Коммутатор не требует питания", False), ("Ни в чем", False)], "Интеллектуальная пересылка.", "Easy", "Conceptual Analysis"),
        ("Что такое Store-and-Forward коммутация?", [("Прием всего фрейма перед пересылкой", True), ("Пересылка сразу после получения заголовка", False), ("Хранение данных на диске", False), ("Тип кабеля", False)], "Метод проверки ошибок.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Cut-Through коммутация?", [("Начало пересылки сразу после адреса назначения", True), ("Отрезание части данных", False), ("Быстрое удаление ошибок", False), ("Сверхмедленная работа", False)], "Минимальная задержка.", "Intermediate", "Conceptual Analysis"),
        ("Какова основная функция протокола STP (802.1D)?", [("Блокировка избыточных путей для исключения петель", True), ("Увеличение пропускной способности", False), ("Настройка VLAN", False), ("Шифрование трафика", False)], "Устранение L2 циклов.", "Hard", "Conceptual Analysis"),
        ("Что такое BPDU?", [("Служебные пакеты протокола STP", True), ("Тип вируса", False), ("Сетевой пароль", False), ("Марка коммутатора", False)], "Bridge Protocol Data Unit.", "Hard", "Conceptual Analysis"),
        ("Какое состояние порта STP означает, что он не передает данные?", [("Blocking", True), ("Forwarding", False), ("Listening", False), ("Learning", False)], "Заблокированный порт.", "Intermediate", "Conceptual Analysis"),
        ("Что такое PortFast?", [("Мгновенный переход порта в состояние Forwarding", True), ("Очень быстрый разъем", False), ("Ускорение интернета", False), ("Тип кабеля", False)], "Для подключения конечных устройств.", "Hard", "Conceptual Analysis"),
        ("Что такое агрегация каналов (EtherChannel/LACP)?", [("Объединение нескольких линий в одну логическую", True), ("Поломка кабеля", False), ("Разделение сети", False), ("Тип антенны", False)], "Увеличение полосы и надежности.", "Hard", "Conceptual Analysis"),
        ("Какой протокол используется для динамического согласования EtherChannel?", [("LACP (802.3ad)", True), ("STP", False), ("VLAN", False), ("HTTP", False)], "Link Aggregation Control.", "Hard", "Conceptual Analysis"),
        ("Что такое домен коллизий (Collision Domain)?", [("Сегмент, где возможны коллизии", True), ("Имя сайта", False), ("Группа серверов", False), ("Тип роутера", False)], "Ограничение полудуплекса.", "Intermediate", "Conceptual Analysis"),
        ("Сколько доменов коллизий у 24-портового коммутатора?", [("24", True), ("1", False), ("0", False), ("48", False)], "Каждый порт - свой домен.", "Intermediate", "Conceptual Analysis"),
        ("Что такое уровень доступа (Access Layer) в иерархической модели?", [("Место подключения конечных пользователей", True), ("Ядро сети", False), ("Серверная комната", False), ("Интернет-шлюз", False)], "Нижний уровень иерархии.", "Intermediate", "Conceptual Analysis"),
        ("Что такое уровень распределения (Distribution Layer)?", [("Агрегация каналов от уровня доступа и применение политик", True), ("Просто кабели", False), ("Подключение к провайдеру", False), ("Место отдыха админов", False)], "Средний уровень иерархии.", "Intermediate", "Conceptual Analysis"),
        ("Что такое уровень ядра (Core Layer)?", [("Высокоскоростная магистраль сети", True), ("Место для Wi-Fi", False), ("Подключение принтеров", False), ("Нижний уровень", False)], "Верхний уровень иерархии.", "Intermediate", "Conceptual Analysis"),
        ("Что такое L3 Switch (Коммутатор 3 уровня)?", [("Коммутатор, умеющий выполнять маршрутизацию", True), ("Коммутатор с 3 портами", False), ("Очень старый коммутатор", False), ("Тип роутера", False)], "Сочетание L2 и L3.", "Intermediate", "Conceptual Analysis"),
        ("Для чего используется зеркалирование портов (SPAN)?", [("Анализ трафика без прерывания работы", True), ("Удвоение скорости", False), ("Защита от воды", False), ("Красивый дизайн", False)], "Мониторинг сети.", "Hard", "Conceptual Analysis"),
        ("Что такое Frame Check Sequence (FCS)?", [("Поле для проверки целостности фрейма", True), ("Имя кадра", False), ("Скорость передачи", False), ("Тип разъема", False)], "Контрольная сумма.", "Intermediate", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in switching_questions:
        add_question('switching', text, choices, hint, diff, cat)

    # 8. Маршрутизация (routing) - 20 вопросов
    routing_questions = [
        ("Какова основная задача маршрутизатора?", [("Выбор наилучшего пути для доставки пакетов", True), ("Соединение компьютеров в LAN", False), ("Печать документов", False), ("Зарядка устройств", False)], "Логика L3.", "Easy", "Conceptual Analysis"),
        ("Что такое таблица маршрутизации?", [("Список известных сетей и путей к ним", True), ("Список имен пользователей", False), ("Таблица MAC-адресов", False), ("История браузера", False)], "База данных роутера.", "Easy", "Conceptual Analysis"),
        ("Что такое статическая маршрутизация?", [("Маршруты, заданные администратором вручную", True), ("Маршруты, которые не работают", False), ("Автоматические маршруты", False), ("Маршруты через спутник", False)], "Ручное управление.", "Intermediate", "Conceptual Analysis"),
        ("Что такое динамическая маршрутизация?", [("Автоматическое изучение путей через протоколы", True), ("Очень быстрая маршрутизация", False), ("Маршрутизация во время движения", False), ("Случайный выбор пути", False)], "Использование протоколов.", "Intermediate", "Conceptual Analysis"),
        ("Что такое метрика (Metric) в маршрутизации?", [("Значение, используемое для выбора лучшего пути", True), ("Длина кабеля в метрах", False), ("Вес роутера", False), ("Количество портов", False)], "Критерий выбора.", "Intermediate", "Conceptual Analysis"),
        ("Что такое административное расстояние (Administrative Distance)?", [("Показатель надежности источника маршрута", True), ("Расстояние до офиса админа", False), ("Длина пароля", False), ("Скорость канала", False)], "Приоритет протоколов.", "Hard", "Conceptual Analysis"),
        ("Какой протокол относится к дистанционно-векторным (Distance Vector)?", [("RIP", True), ("OSPF", False), ("IS-IS", False), ("BGP", False)], "Считает переходы (hops).", "Intermediate", "Conceptual Analysis"),
        ("Какой протокол относится к протоколам состояния канала (Link-State)?", [("OSPF", True), ("RIP", False), ("EIGRP", False), ("BGP", False)], "Строит карту сети.", "Intermediate", "Conceptual Analysis"),
        ("Что такое 'хоп' (Hop) в маршрутизации?", [("Прохождение через один промежуточный роутер", True), ("Прыжок кабеля", False), ("Ошибка сети", False), ("Тип пакета", False)], "Количество узлов на пути.", "Easy", "Conceptual Analysis"),
        ("Для чего используется маршрут по умолчанию (0.0.0.0/0)?", [("Для отправки трафика в неизвестные сети (интернет)", True), ("Для тестирования", False), ("Для всех локальных компьютеров", False), ("Он не нужен", False)], "Gateway of last resort.", "Intermediate", "Conceptual Analysis"),
        ("Что такое автономная система (AS)?", [("Группа сетей под единым управлением", True), ("Компьютер без человека", False), ("Робот-пылесос", False), ("Тип роутера", False)], "Используется в BGP.", "Hard", "Conceptual Analysis"),
        ("Какой протокол используется для маршрутизации между AS в интернете?", [("BGP", True), ("OSPF", False), ("RIP", False), ("EIGRP", False)], "Exterior Gateway Protocol.", "Hard", "Conceptual Analysis"),
        ("Что такое петля маршрутизации (Routing Loop)?", [("Бесконечная циркуляция пакета между роутерами", True), ("Свернутый кабель", False), ("Тип антенны", False), ("Красивый узел", False)], "Проблема сходимости.", "Intermediate", "Conceptual Analysis"),
        ("Для чего нужен протокол ARP на роутере?", [("Для определения MAC-адреса следующего узла", True), ("Для раздачи IP", False), ("Для защиты", False), ("Для DNS", False)], "Связь L3 и L2.", "Intermediate", "Conceptual Analysis"),
        ("Что такое разделение горизонта (Split Horizon)?", [("Метод предотвращения петель в RIP", True), ("Линия моря", False), ("Настройка экрана", False), ("Тип кабеля", False)], "Не слать обратно то, что узнал.", "Hard", "Conceptual Analysis"),
        ("Какое устройство является 'шлюзом' для компьютеров в LAN?", [("Интерфейс роутера в этой сети", True), ("Коммутатор", False), ("Принтер", False), ("Другой компьютер", False)], "Default Gateway.", "Easy", "Conceptual Analysis"),
        ("Что такое Router on a Stick?", [("Маршрутизация между VLAN через один интерфейс", True), ("Роутер на палке", False), ("Сломанный роутер", False), ("Тип антенны", False)], "Использование сабинтерфейсов.", "Hard", "Conceptual Analysis"),
        ("Что такое сабинтерфейс (Subinterface)?", [("Виртуальное разделение физического порта", True), ("Маленький разъем", False), ("Запасной порт", False), ("Тип меню", False)], "Для работы с VLAN.", "Hard", "Conceptual Analysis"),
        ("Какой протокол выбирает путь на основе стоимости (Cost)?", [("OSPF", True), ("RIP", False), ("BGP", False), ("Static", False)], "Open Shortest Path First.", "Intermediate", "Conceptual Analysis"),
        ("Что такое сходимость (Convergence)?", [("Состояние, когда все роутеры имеют одинаковую информацию", True), ("Поломка сети", False), ("Слияние компаний", False), ("Тип разъема", False)], "Завершение обновления таблиц.", "Hard", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in routing_questions:
        add_question('routing', text, choices, hint, diff, cat)

    # 9. Безопасность (security) - 20 вопросов
    security_questions = [
        ("Что такое брандмауэр (Firewall)?", [("Устройство или ПО для фильтрации трафика", True), ("Программа для ускорения интернета", False), ("Тип кабеля", False), ("Антивирус для флешек", False)], "Межсетевой экран.", "Easy", "Conceptual Analysis"),
        ("Что такое ACL (Access Control List)?", [("Список правил доступа на основе адресов и портов", True), ("Список друзей в соцсети", False), ("Тип жесткого диска", False), ("Протокол почты", False)], "Управление доступом.", "Intermediate", "Conceptual Analysis"),
        ("Что такое VPN?", [("Виртуальная частная сеть для защищенного туннеля", True), ("Очень быстрая сеть", False), ("Программа для взлома", False), ("Тип модема", False)], "Virtual Private Network.", "Easy", "Conceptual Analysis"),
        ("Что такое IDS (Intrusion Detection System)?", [("Система обнаружения вторжений", True), ("Система очистки диска", False), ("Система полива", False), ("Система защиты от пыли", False)], "Мониторинг атак.", "Intermediate", "Conceptual Analysis"),
        ("В чем отличие IPS от IDS?", [("IPS может блокировать атаку, а IDS только сообщает", True), ("IPS медленнее", False), ("IPS работает только в облаке", False), ("Ни в чем", False)], "Intrusion Prevention.", "Intermediate", "Conceptual Analysis"),
        ("Что такое DoS-атака?", [("Атака с целью отказа в обслуживании", True), ("Попытка украсть пароль", False), ("Тип операционной системы", False), ("Сетевой кабель", False)], "Denial of Service.", "Easy", "Conceptual Analysis"),
        ("Что такое DDoS-атака?", [("Распределенная DoS-атака с множества устройств", True), ("Двойная защита", False), ("Очень быстрая атака", False), ("Атака через почту", False)], "Distributed DoS.", "Easy", "Conceptual Analysis"),
        ("Что такое фишинг (Phishing)?", [("Создание поддельных сайтов для кражи данных", True), ("Ловля рыбы в интернете", False), ("Тип вируса", False), ("Сетевой протокол", False)], "Социальная инженерия.", "Easy", "Conceptual Analysis"),
        ("Что такое вредоносное ПО (Malware)?", [("Любое ПО, созданное для нанесения вреда", True), ("Плохо написанная программа", False), ("Игра", False), ("Драйвер", False)], "Общий термин.", "Easy", "Conceptual Analysis"),
        ("Что такое шифрование (Encryption)?", [("Преобразование данных в нечитаемый вид", True), ("Сжатие файлов", False), ("Перевод на другой язык", False), ("Удаление данных", False)], "Защита конфиденциальности.", "Easy", "Conceptual Analysis"),
        ("В чем разница между симметричным и асимметричным шифрованием?", [("В асимметричном используются два ключа: публичный и приватный", True), ("Симметричное надежнее", False), ("Асимметричное быстрее", False), ("Разницы нет", False)], "Криптографические основы.", "Hard", "Conceptual Analysis"),
        ("Что такое DMZ (Демилитаризованная зона)?", [("Сегмент сети для публичных сервисов", True), ("Место без компьютеров", False), ("Граница между странами", False), ("Тип роутера", False)], "Буферная зона.", "Intermediate", "Conceptual Analysis"),
        ("Что такое аутентификация?", [("Проверка подлинности пользователя (кто вы?)", True), ("Проверка прав доступа (что вам можно?)", False), ("Ввод текста", False), ("Тип пароля", False)], "Authentication.", "Intermediate", "Conceptual Analysis"),
        ("Что такое авторизация?", [("Проверка прав доступа (что вам можно?)", True), ("Проверка подлинности (кто вы?)", False), ("Регистрация", False), ("Вход в систему", False)], "Authorization.", "Intermediate", "Conceptual Analysis"),
        ("Что такое двухфакторная аутентификация (2FA)?", [("Использование двух разных способов подтверждения", True), ("Ввод пароля дважды", False), ("Использование двух компьютеров", False), ("Смена пароля раз в месяц", False)], "Повышенная безопасность.", "Easy", "Conceptual Analysis"),
        ("Что такое RADIUS?", [("Протокол для централизованной аутентификации", True), ("Геометрическая фигура", False), ("Тип антенны", False), ("Расстояние действия Wi-Fi", False)], "AAA сервис.", "Hard", "Conceptual Analysis"),
        ("Что такое социальная инженерия?", [("Манипуляция людьми для получения данных", True), ("Проектирование соцсетей", False), ("Общение с коллегами", False), ("Тип вируса", False)], "Психологические атаки.", "Intermediate", "Conceptual Analysis"),
        ("Что такое атака Man-in-the-Middle (MitM)?", [("Перехват и подмена данных между узлами", True), ("Человек, стоящий между серверами", False), ("Тип брандмауэра", False), ("Программная ошибка", False)], "Человек посередине.", "Intermediate", "Conceptual Analysis"),
        ("Что такое SSL/TLS?", [("Протоколы для защиты соединений в интернете", True), ("Тип кабеля", False), ("Протоколы почты", False), ("Вид вируса", False)], "Основа HTTPS.", "Intermediate", "Conceptual Analysis"),
        ("Какая основная задача AAA (Authentication, Authorization, Accounting)?", [("Управление доступом и учет действий", True), ("Ускорение сети", False), ("Поиск вирусов", False), ("Резервное копирование", False)], "Три столпа безопасности.", "Hard", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in security_questions:
        add_question('security', text, choices, hint, diff, cat)

    # 10. Беспроводные сети (wireless) - 20 вопросов
    wireless_questions = [
        ("Какой стандарт описывает беспроводные локальные сети (Wi-Fi)?", [("IEEE 802.11", True), ("IEEE 802.3", False), ("IEEE 802.15", False), ("IEEE 802.1", False)], "Стандарт Wi-Fi.", "Easy", "Conceptual Analysis"),
        ("На каких частотах работает большинство сетей Wi-Fi?", [("2.4 ГГц и 5 ГГц", True), ("900 МГц", False), ("10 ГГц", False), ("60 ГГц", False)], "Основные диапазоны.", "Easy", "Conceptual Analysis"),
        ("Что такое SSID?", [("Название беспроводной сети", True), ("Пароль от Wi-Fi", False), ("Тип антенны", False), ("Адрес роутера", False)], "Service Set Identifier.", "Easy", "Conceptual Analysis"),
        ("Какое устройство является центральным в инфраструктурной Wi-Fi сети?", [("Точка доступа (Access Point)", True), ("Клавиатура", False), ("Принтер", False), ("Смартфон", False)], "AP.", "Easy", "Conceptual Analysis"),
        ("Что такое WPA2?", [("Протокол безопасности и шифрования Wi-Fi", True), ("Модель роутера", False), ("Тип антенны", False), ("Скорость передачи", False)], "Wi-Fi Protected Access 2.", "Intermediate", "Conceptual Analysis"),
        ("В чем преимущество частоты 5 ГГц перед 2.4 ГГц?", [("Выше скорость и меньше помех", True), ("Больше дальность действия", False), ("Проходит сквозь стены лучше", False), ("Дешевле оборудование", False)], "Сравнение диапазонов.", "Intermediate", "Conceptual Analysis"),
        ("Что такое MIMO?", [("Использование нескольких антенн для увеличения скорости", True), ("Тип шифрования", False), ("Название роутера", False), ("Вид вируса", False)], "Multiple Input Multiple Output.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Ad-Hoc режим в Wi-Fi?", [("Соединение устройств напрямую без точки доступа", True), ("Режим максимальной скорости", False), ("Режим скрытой сети", False), ("Тип шифрования", False)], "Peer-to-peer Wi-Fi.", "Intermediate", "Conceptual Analysis"),
        ("Что такое роуминг в беспроводных сетях?", [("Переключение между точками доступа без потери связи", True), ("Платный интернет за границей", False), ("Поиск Wi-Fi", False), ("Смена пароля", False)], "Бесшовное покрытие.", "Intermediate", "Conceptual Analysis"),
        ("Что такое затухание (Attenuation)?", [("Ослабление сигнала при удалении или через препятствия", True), ("Усиление сигнала", False), ("Смена частоты", False), ("Тип антенны", False)], "Потеря мощности.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Bluetooth?", [("Протокол для персональных сетей (PAN) на малых расстояниях", True), ("Замена Wi-Fi", False), ("Тип наушников", False), ("Сетевой кабель", False)], "IEEE 802.15.1.", "Easy", "Conceptual Analysis"),
        ("Для чего используется контроллер беспроводной сети (WLC)?", [("Централизованное управление множеством точек доступа", True), ("Зарядка ноутбуков", False), ("Увеличение дальности одной AP", False), ("Замена роутера", False)], "Wireless LAN Controller.", "Hard", "Conceptual Analysis"),
        ("Что такое Beamforming?", [("Направленная передача сигнала в сторону клиента", True), ("Красивый дизайн роутера", False), ("Формирование пароля", False), ("Тип кабеля", False)], "Технология фокусировки сигнала.", "Hard", "Conceptual Analysis"),
        ("Какое шифрование считается самым современным и надежным для Wi-Fi?", [("WPA3", True), ("WEP", False), ("WPA", False), ("WPA2", False)], "Новый стандарт.", "Intermediate", "Conceptual Analysis"),
        ("Почему WEP считается небезопасным?", [("Легко взламывается из-за слабых алгоритмов", True), ("Слишком длинный пароль", False), ("Работает только на 2.4 ГГц", False), ("Старый разъем", False)], "Уязвимость протокола.", "Intermediate", "Conceptual Analysis"),
        ("Что такое диапазон 6 ГГц в Wi-Fi 6E?", [("Новый свободный диапазон для сверхвысоких скоростей", True), ("Частота микроволновки", False), ("Запрещенная частота", False), ("Частота для радио", False)], "Wi-Fi 6E.", "Hard", "Conceptual Analysis"),
        ("Что такое захваченный портал (Captive Portal)?", [("Страница авторизации при подключении к публичному Wi-Fi", True), ("Секретный вход в сеть", False), ("Тип вируса", False), ("Сетевой шкаф", False)], "Используется в отелях/кафе.", "Intermediate", "Conceptual Analysis"),
        ("Что такое PoE в контексте точек доступа?", [("Питание AP через сетевой кабель", True), ("Беспроводная зарядка", False), ("Скорость интернета", False), ("Тип антенны", False)], "Power over Ethernet.", "Easy", "Conceptual Analysis"),
        ("Что такое коэффициент усиления антенны (Gain)?", [("Способность антенны направлять сигнал", True), ("Вес антенны", False), ("Цвет антенны", False), ("Количество портов", False)], "Измеряется в dBi.", "Intermediate", "Conceptual Analysis"),
        ("Что такое интерференция (Interference)?", [("Наложение радиоволн, создающее помехи", True), ("Улучшение связи", False), ("Тип шифрования", False), ("Настройка роутера", False)], "Проблема плотных сетей.", "Intermediate", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in wireless_questions:
        add_question('wireless', text, choices, hint, diff, cat)

    # 11. Облачные технологии (cloud) - 20 вопросов
    cloud_questions = [
        ("Что такое облачные вычисления (Cloud Computing)?", [("Предоставление ресурсов через интернет по запросу", True), ("Компьютеры в небе", False), ("Прогноз погоды", False), ("Тип Wi-Fi", False)], "Аренда мощностей.", "Easy", "Conceptual Analysis"),
        ("Что такое SaaS?", [("Программное обеспечение как услуга (напр. Google Drive)", True), ("Сервер как услуга", False), ("Кабель как услуга", False), ("Тип вируса", False)], "Software as a Service.", "Easy", "Conceptual Analysis"),
        ("Что такое IaaS?", [("Инфраструктура как услуга (напр. AWS EC2)", True), ("Интернет как услуга", False), ("Игра как услуга", False), ("Тип роутера", False)], "Infrastructure as a Service.", "Intermediate", "Conceptual Analysis"),
        ("Что такое PaaS?", [("Платформа как услуга (для разработчиков)", True), ("Пароль как услуга", False), ("Принтер как услуга", False), ("Почта как услуга", False)], "Platform as a Service.", "Intermediate", "Conceptual Analysis"),
        ("В чем главное преимущество облаков для бизнеса?", [("Масштабируемость и оплата по факту использования", True), ("Красивый интерфейс", False), ("Бесплатность", False), ("Работа без интернета", False)], "Экономическая выгода.", "Easy", "Conceptual Analysis"),
        ("Что такое публичное облако (Public Cloud)?", [("Инфраструктура, доступная всем желающим", True), ("Облако в парке", False), ("Бесплатный Wi-Fi", False), ("Сайт госуслуг", False)], "Напр. AWS, Azure.", "Easy", "Conceptual Analysis"),
        ("Что такое частное облако (Private Cloud)?", [("Облако для одной конкретной организации", True), ("Личный компьютер", False), ("Скрытая папка", False), ("Домашний сервер", False)], "Повышенная безопасность.", "Intermediate", "Conceptual Analysis"),
        ("Что такое гибридное облако (Hybrid Cloud)?", [("Сочетание частного и публичного облаков", True), ("Облако с дождем", False), ("Облако и кабель", False), ("Два разных провайдера", False)], "Гибкость.", "Intermediate", "Conceptual Analysis"),
        ("Что такое виртуализация?", [("Запуск нескольких ОС на одном физическом сервере", True), ("Компьютерные игры", False), ("Очки виртуальной реальности", False), ("Тип монитора", False)], "Основа облаков.", "Intermediate", "Conceptual Analysis"),
        ("Что такое гипервизор (Hypervisor)?", [("ПО для создания и управления виртуальными машинами", True), ("Очень быстрый процессор", False), ("Главный администратор", False), ("Тип вируса", False)], "VMM.", "Hard", "Conceptual Analysis"),
        ("Что такое эластичность (Elasticity) в облаках?", [("Способность быстро изменять объем ресурсов", True), ("Гибкий кабель", False), ("Мягкий корпус сервера", False), ("Растягивание экрана", False)], "Динамическое масштабирование.", "Intermediate", "Conceptual Analysis"),
        ("Что такое пограничные вычисления (Edge Computing)?", [("Обработка данных ближе к источнику (на краю сети)", True), ("Вычисления на листе бумаги", False), ("Очень опасные вычисления", False), ("Тип браузера", False)], "Снижение задержек.", "Hard", "Conceptual Analysis"),
        ("Что такое Serverless вычисления?", [("Запуск кода без управления серверами (напр. AWS Lambda)", True), ("Работа без электричества", False), ("Работа без интернета", False), ("Тип клавиатуры", False)], "FaaS.", "Hard", "Conceptual Analysis"),
        ("Что такое CDN (Content Delivery Network)?", [("Сеть серверов для быстрой доставки контента", True), ("Телеканал", False), ("Тип кабеля", False), ("Протокол почты", False)], "Ускорение загрузки сайтов.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Multitenancy?", [("Использование ресурсов множеством клиентов одновременно", True), ("Много арендаторов в офисе", False), ("Много кнопок на мыши", False), ("Тип антенны", False)], "Многоарендность.", "Hard", "Conceptual Analysis"),
        ("Какая основная угроза безопасности в облаках?", [("Утечка данных из-за неправильной настройки", True), ("Поломка жесткого диска", False), ("Кража сервера из ЦОД", False), ("Плохая погода", False)], "Человеческий фактор.", "Intermediate", "Conceptual Analysis"),
        ("Что такое ЦОД (Дата-центр)?", [("Здание с серверами и сетевым оборудованием", True), ("Центр обработки документов", False), ("Магазин компьютеров", False), ("Офис провайдера", False)], "Физическая база облаков.", "Easy", "Conceptual Analysis"),
        ("Что такое доступность (Availability) 99.999%?", [("Очень высокая надежность (простой 5 мин в год)", True), ("Цена услуги", False), ("Скорость интернета", False), ("Количество серверов", False)], "Пять девяток.", "Hard", "Conceptual Analysis"),
        ("Что такое контейнеризация (напр. Docker)?", [("Легковесная виртуализация на уровне приложений", True), ("Перевозка серверов в контейнерах", False), ("Тип упаковки", False), ("Сетевой протокол", False)], "Альтернатива виртуальным машинам.", "Hard", "Conceptual Analysis"),
        ("Что такое облачное хранилище?", [("Сервис для хранения файлов в интернете", True), ("Жесткий диск в небе", False), ("Флешка", False), ("Тип памяти в телефоне", False)], "Напр. Dropbox, OneDrive.", "Easy", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in cloud_questions:
        add_question('cloud', text, choices, hint, diff, cat)

    # 12. Клиент-сервер (client_server) - 20 вопросов
    client_server_questions = [
        ("Что такое архитектура клиент-сервер?", [("Модель взаимодействия, где есть поставщик и потребитель услуг", True), ("Два компьютера рядом", False), ("Тип сетевого кабеля", False), ("Название программы", False)], "Разделение ролей.", "Easy", "Conceptual Analysis"),
        ("Какова роль клиента?", [("Запрашивать услуги или данные", True), ("Предоставлять данные всем", False), ("Управлять всей сетью", False), ("Чинить сервер", False)], "Инициатор запроса.", "Easy", "Conceptual Analysis"),
        ("Какова роль сервера?", [("Обрабатывать запросы и предоставлять ресурсы", True), ("Играть в игры", False), ("Выключать интернет", False), ("Печатать документы", False)], "Поставщик услуг.", "Easy", "Conceptual Analysis"),
        ("Что такое HTTP запрос?", [("Сообщение от клиента серверу", True), ("Сообщение от сервера клиенту", False), ("Тип вируса", False), ("Сетевой кабель", False)], "Request.", "Easy", "Conceptual Analysis"),
        ("Что такое HTTP ответ?", [("Сообщение от сервера клиенту", True), ("Сообщение от клиента серверу", False), ("Ошибка Windows", False), ("Тип антенны", False)], "Response.", "Easy", "Conceptual Analysis"),
        ("Что означает статус-код 200 в HTTP?", [("Успешно", True), ("Ошибка сервера", False), ("Страница не найдена", False), ("Доступ запрещен", False)], "OK.", "Intermediate", "Conceptual Analysis"),
        ("Что означает статус-код 404?", [("Страница не найдена", True), ("Все хорошо", False), ("Ошибка сервера", False), ("Перенаправление", False)], "Not Found.", "Easy", "Conceptual Analysis"),
        ("Что означает статус-код 500?", [("Внутренняя ошибка сервера", True), ("Ошибка клиента", False), ("Успех", False), ("Нет интернета", False)], "Internal Server Error.", "Intermediate", "Conceptual Analysis"),
        ("Что такое API?", [("Интерфейс для взаимодействия программ", True), ("Тип монитора", False), ("Имя сервера", False), ("Сетевой пароль", False)], "Application Programming Interface.", "Intermediate", "Conceptual Analysis"),
        ("Что такое REST?", [("Стиль архитектуры для веб-сервисов", True), ("Отдых сервера", False), ("Тип кабеля", False), ("Протокол почты", False)], "Representational State Transfer.", "Hard", "Conceptual Analysis"),
        ("Для чего используется база данных на сервере?", [("Для надежного хранения и поиска информации", True), ("Для ускорения Wi-Fi", False), ("Для защиты от пыли", False), ("Для красоты", False)], "Хранилище данных.", "Easy", "Conceptual Analysis"),
        ("Что такое SQL?", [("Язык запросов к базам данных", True), ("Тип сервера", False), ("Сетевой протокол", False), ("Имя администратора", False)], "Structured Query Language.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Frontend?", [("Часть приложения, которую видит пользователь", True), ("Задняя часть сервера", False), ("Провода в стене", False), ("Сетевая карта", False)], "Клиентская сторона.", "Easy", "Conceptual Analysis"),
        ("Что такое Backend?", [("Серверная часть приложения", True), ("Экран монитора", False), ("Мышка", False), ("Клавиатура", False)], "Логика на сервере.", "Easy", "Conceptual Analysis"),
        ("Что такое балансировщик нагрузки (Load Balancer)?", [("Устройство для распределения запросов между серверами", True), ("Весы для компьютеров", False), ("Тип аккумулятора", False), ("Сетевой фильтр", False)], "Обеспечение отказоустойчивости.", "Hard", "Conceptual Analysis"),
        ("Что такое кэширование (Caching)?", [("Сохранение копий данных для быстрого доступа", True), ("Удаление старых файлов", False), ("Заработок денег в сети", False), ("Тип памяти", False)], "Повышение скорости.", "Intermediate", "Conceptual Analysis"),
        ("Что такое Stateful взаимодействие?", [("Сервер помнит состояние сессии клиента", True), ("Сервер всегда занят", False), ("Клиент всегда прав", False), ("Тип кабеля", False)], "Состояние сессии.", "Hard", "Conceptual Analysis"),
        ("Что такое Stateless взаимодействие (напр. HTTP)?", [("Каждый запрос независим и содержит все данные", True), ("Сервер не работает", False), ("Нет правил", False), ("Тип Wi-Fi", False)], "Без сохранения состояния.", "Hard", "Conceptual Analysis"),
        ("Что такое прокси-сервер?", [("Посредник между клиентом и сервером", True), ("Замена роутера", False), ("Сетевой кабель", False), ("Тип монитора", False)], "Proxy.", "Intermediate", "Conceptual Analysis"),
        ("Что такое многоуровневая архитектура (N-tier)?", [("Разделение приложения на уровни (представление, логика, данные)", True), ("Много компьютеров в ряд", False), ("Тип шкафа", False), ("Сложная схема кабелей", False)], "Масштабируемость.", "Hard", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in client_server_questions:
        add_question('client_server', text, choices, hint, diff, cat)

    # 13. Итоговый проект (final_project) - 20 вопросов
    final_questions = [
        ("С чего начинается проектирование сети?", [("С анализа требований и целей бизнеса", True), ("С покупки самых дорогих роутеров", False), ("С прокладки кабелей", False), ("С выбора обоев в серверную", False)], "Планирование.", "Easy", "Conceptual Analysis"),
        ("Что такое логическая топология?", [("Схема движения данных в сети", True), ("Внешний вид кабелей", False), ("План здания", False), ("Список сотрудников", False)], "Логическая схема.", "Intermediate", "Conceptual Analysis"),
        ("Что такое физическая топология?", [("Физическое расположение устройств и кабелей", True), ("Схема IP-адресов", False), ("Тип программ", False), ("Настройка Wi-Fi", False)], "Физическая схема.", "Easy", "Conceptual Analysis"),
        ("Для чего используется избыточность (Redundancy) в проектах?", [("Для обеспечения работы при отказах", True), ("Для траты лишних денег", False), ("Для красоты", False), ("Для замедления сети", False)], "Отказоустойчивость.", "Intermediate", "Conceptual Analysis"),
        ("Что такое спецификация оборудования?", [("Список необходимых устройств с характеристиками", True), ("Инструкция по включению", False), ("Гарантийный талон", False), ("Рекламный буклет", False)], "Документация.", "Easy", "Conceptual Analysis"),
        ("Какое устройство является ядром (Core) корпоративной сети?", [("Высокопроизводительный коммутатор L3", True), ("Обычный Wi-Fi роутер", False), ("Принтер", False), ("Ноутбук директора", False)], "Центральный узел.", "Intermediate", "Conceptual Analysis"),
        ("Что такое масштабируемость проекта?", [("Возможность легкого расширения сети в будущем", True), ("Размер чертежа", False), ("Количество цветов на схеме", False), ("Вес оборудования", False)], "Scalability.", "Intermediate", "Conceptual Analysis"),
        ("Для чего нужно разделение на VLAN в корпоративной сети?", [("Для безопасности и уменьшения бродкаст-трафика", True), ("Для красоты", False), ("Для увеличения скорости интернета", False), ("Для экономии кабеля", False)], "Сегментация.", "Intermediate", "Conceptual Analysis"),
        ("Что такое сетевой шкаф (Rack)?", [("Конструкция для размещения оборудования", True), ("Место для одежды", False), ("Шкаф с книгами", False), ("Тип роутера", False)], "Монтаж оборудования.", "Easy", "Conceptual Analysis"),
        ("Для чего используется ИБП (UPS) в серверной?", [("Для работы оборудования при отключении питания", True), ("Для защиты от пыли", False), ("Для красоты", False), ("Для интернета", False)], "Uninterruptible Power Supply.", "Easy", "Conceptual Analysis"),
        ("Что такое инвентаризация сети?", [("Учет всех устройств и их параметров", True), ("Покупка новых мышек", False), ("Уборка в серверной", False), ("Смена паролей", False)], "Учет ресурсов.", "Intermediate", "Conceptual Analysis"),
        ("Что такое QoS (Quality of Service)?", [("Приоритизация важного трафика (напр. голоса)", True), ("Качество сборки роутера", False), ("Вежливость админа", False), ("Скорость скачивания", False)], "Управление качеством.", "Hard", "Conceptual Analysis"),
        ("Для чего нужно тестирование сети после монтажа?", [("Для проверки соответствия проекту и отсутствия ошибок", True), ("Чтобы просто включить", False), ("Для отчета", False), ("Для красоты", False)], "Верификация.", "Easy", "Conceptual Analysis"),
        ("Что такое исполнительная документация?", [("Фактические схемы и настройки после завершения работ", True), ("Приказ директора", False), ("Журнал посещений", False), ("Тип кабеля", False)], "Итоговые документы.", "Intermediate", "Conceptual Analysis"),
        ("Какая технология позволяет объединить удаленные офисы?", [("VPN / MPLS", True), ("Длинный кабель", False), ("Wi-Fi", False), ("Флешка", False)], "Связь филиалов.", "Intermediate", "Conceptual Analysis"),
        ("Что такое мониторинг сети (NMS)?", [("Система для слежения за состоянием устройств", True), ("Камеры наблюдения", False), ("Слежка за сотрудниками", False), ("Тип телевизора", False)], "Управление сетью.", "Intermediate", "Conceptual Analysis"),
        ("Что такое политика безопасности?", [("Набор правил и процедур защиты данных", True), ("Пароль на компьютере", False), ("Охранник на входе", False), ("Тип антивируса", False)], "Основа защиты.", "Intermediate", "Conceptual Analysis"),
        ("Для чего нужно резервное копирование (Backup) конфигураций?", [("Для быстрого восстановления после сбоя", True), ("Для коллекции", False), ("Для экономии места", False), ("Для красоты", False)], "Безопасность настроек.", "Easy", "Conceptual Analysis"),
        ("Что такое жизненный цикл сети?", [("Период от проектирования до замены оборудования", True), ("Время работы роутера до поломки", False), ("Рабочий день админа", False), ("Время скачивания файла", False)], "Этапы существования.", "Intermediate", "Conceptual Analysis"),
        ("Какова финальная цель любого сетевого проекта?", [("Обеспечение надежной и безопасной передачи данных", True), ("Покупка самого красивого шкафа", False), ("Установка всех возможных программ", False), ("Прокладка 100 км кабеля", False)], "Главная цель.", "Easy", "Conceptual Analysis"),
    ]

    for text, choices, hint, diff, cat in final_questions:
        add_question('final_project', text, choices, hint, diff, cat)

    print("Added questions for security, wireless, cloud, client_server, and final_project.")




if __name__ == '__main__':
    run()
