import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Module, Question, Choice

def add_question(module_slug, text, choices, hint='', difficulty='Intermediate', category='Conceptual Analysis', q_type='multiple_choice', explanation=''):
    try:
        module = Module.objects.get(slug=module_slug)
        question, created = Question.objects.get_or_create(
            module=module,
            text=text,
            defaults={
                'hint': hint, 
                'difficulty': difficulty, 
                'category': category,
                'type': q_type,
                'explanation': explanation
            }
        )
        if created:
            for choice_data in choices:
                if isinstance(choice_data, tuple):
                    choice_text, is_correct = choice_data[0], choice_data[1]
                    pair_text = choice_data[2] if len(choice_data) > 2 else ''
                else:
                    choice_text, is_correct, pair_text = choice_data, True, ''
                
                Choice.objects.get_or_create(
                    question=question, 
                    text=choice_text, 
                    defaults={'is_correct': is_correct, 'pair_text': pair_text}
                )
            return True
        return False
    except Module.DoesNotExist:
        print(f"Module {module_slug} not found.")
        return False

def run():
    # Cleanup
    Question.objects.all().delete() 
    
    # 1. Введение (introduction)
    intro_questions = [
        ("Что такое компьютерная сеть?", [("Группа соединенных компьютеров для обмена данными", True), ("Один мощный компьютер", False)], "Базовое определение.", "Easy", "Conceptual Analysis", "multiple_choice", "Сеть — это прежде всего взаимодействие устройств."),
        ("Расположите типы сетей от меньшей к большей по охвату:", [("PAN", True), ("LAN", True), ("MAN", True), ("WAN", True)], "От персональной к глобальной.", "Intermediate", "Conceptual Analysis", "sorting", "PAN (Personal), LAN (Local), MAN (Metropolitan), WAN (Wide)."),
        ("Сопоставьте термин и описание:", [("Узел", True, "Любое устройство в сети"), ("Протокол", True, "Набор правил"), ("Топология", True, "Схема связей")], "Базовые понятия.", "Intermediate", "Conceptual Analysis", "matching", "Эти термины — фундамент сетевых технологий."),
        ("Как называется глобальная сеть, объединяющая миллионы устройств по всему миру?", [("Internet", True), ("интернет", True)], "Пишите на русском или английском.", "Easy", "Conceptual Analysis", "text_input", "Интернет — это 'сеть сетей'."),
    ]
    for q in intro_questions: add_question('introduction', *q)

    # 2. Модель OSI (osi_model)
    osi_questions = [
        ("Сколько уровней в модели OSI?", [("7", True), ("5", False)], "Стандарт ISO.", "Easy", "Conceptual Analysis", "multiple_choice", "Модель OSI состоит ровно из 7 уровней."),
        ("Расположите уровни OSI сверху вниз:", [("Прикладной", True), ("Представительский", True), ("Сеансовый", True), ("Транспортный", True), ("Сетевой", True), ("Канальный", True), ("Физический", True)], "Топ-даун.", "Hard", "Conceptual Analysis", "sorting", "Стандартный порядок обработки данных."),
        ("Сопоставьте уровень и его PDU:", [("Транспортный", True, "Сегмент"), ("Сетевой", True, "Пакет"), ("Канальный", True, "Фрейм")], "Единицы данных.", "Intermediate", "Conceptual Analysis", "matching", "На каждом уровне данные имеют свое название."),
    ]
    for q in osi_questions: add_question('osi_model', *q)

    # 3. Стек TCP/IP (tcp_ip)
    tcp_questions = [
        ("Какой протокол обеспечивает надежную доставку?", [("TCP", True), ("UDP", False)], "Установка соединения.", "Easy", "Conceptual Analysis", "multiple_choice", "TCP гарантирует доставку."),
        ("Что такое трехстороннее рукопожатие?", [("SYN", True), ("SYN-ACK", True), ("ACK", True)], "Этапы установления TCP.", "Intermediate", "Conceptual Analysis", "sorting", "Процесс SYN -> SYN-ACK -> ACK."),
    ]
    for q in tcp_questions: add_question('tcp_ip', *q)

    # 4. IP-адресация (ip_addressing)
    ip_questions = [
        ("Сколько бит в адресе IPv4?", [("32", True), ("128", False)], "Четыре октета.", "Easy", "Conceptual Analysis", "multiple_choice", "IPv4 использует 32-битную адресацию."),
        ("Введите Loopback адрес IPv4:", [("127.0.0.1", True)], "Тестирование стека.", "Easy", "Conceptual Analysis", "text_input", "Локальный адрес хоста."),
    ]
    for q in ip_questions: add_question('ip_addressing', *q)

    # Добавляем базовые вопросы для остальных модулей (чтобы не было пусто)
    other_modules = [
        'lan', 'switching', 'routing', 'protocols', 'security', 
        'wireless', 'cloud', 'client_server', 'final_project'
    ]
    for slug in other_modules:
        add_question(slug, f"Тестовый вопрос для модуля {slug}", [("Правильный ответ", True), ("Неправильный ответ", False)], "Подсказка", "Easy", "General", "multiple_choice", "Объяснение")

    print("Questions database updated successfully with new types and explanations.")

if __name__ == '__main__':
    run()
