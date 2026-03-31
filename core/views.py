from django.shortcuts import render
from django.utils.translation import gettext as _

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def legal_view(request, page_type):
    """Отображение юридических страниц (политика конфиденциальности и т.д.)"""
    pages = {
        'privacy': _('Политика конфиденциальности'),
        'terms': _('Условия использования'),
        'cookies': _('Политика использования cookies'),
    }
    context = {
        'title': pages.get(page_type, _('Юридическая информация')),
        'page_type': page_type
    }
    return render(request, 'core/legal.html', context)
