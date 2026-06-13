
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'computer_networks.settings')
django.setup()

from courses.models import Module, Question, Choice


def run():
    Question.objects.all().delete()
    
    modules = list(Module.objects.all().order_by('order'))
    if not modules:
        print("No modules found")
        return

    for idx, module in enumerate(modules):
        module_num = idx + 1
        is_final = (idx == 12)  # 13th module
        count = 20 if is_final else 10

        for q_idx in range(count):
            q_text = f"Вопрос {q_idx + 1} для модуля {module_num} ({module.name})"
            q_text_kk = f"{module_num} модульге арналған {q_idx + 1} сұрақ"

            question = Question.objects.create(
                module=module,
                text=q_text,
                text_kk=q_text_kk,
                difficulty="Easy",
                type="multiple_choice"
            )

            for c_idx in range(4):
                choice_text = f"Вариант {c_idx + 1}"
                choice_text_kk = f"{c_idx + 1}- нұсқа"
                Choice.objects.create(
                    question=question,
                    text=choice_text,
                    text_kk=choice_text_kk,
                    is_correct=(c_idx == 0)
                )

    print("Questions added successfully!")


if __name__ == '__main__':
    run()
