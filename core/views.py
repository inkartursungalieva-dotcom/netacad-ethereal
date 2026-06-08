from django.shortcuts import render
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import httpx
import os
import logging

logger = logging.getLogger(__name__)

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

def api_docs_view(request):
    """Отображение документации API"""
    return render(request, 'core/api_docs.html')

@csrf_exempt
async def ai_chat_api(request):
    """Гибридный ИИ: API DeepSeek с локальным отказоустойчивым режимом (асинхронный)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '')
        
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        
        # Если ключ есть, пробуем реальный ИИ через DeepSeek
        if api_key:
            system_prompt = (
                "Ты — Computer Networks AI, экспертный помощник обучающей платформы по компьютерным сетям. "
                "Твоя задача: помогать студентам и преподавателям. "
                "Ты знаешь про 13 модулей курса (введение, OSI, IP, маршрутизация, коммутация, безопасность, беспроводные сети, облака и т.д.), "
                "про сетевой конструктор, лабораторию OSI и IP-калькулятор. "
                "Отвечай вежливо, профессионально на русском или казахском языке. "
                "Если вопрос касается топологии сети, предложи использовать наш Сетевой конструктор."
            )

            url = "https://api.deepseek.com/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                "stream": False
            }

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                
                if response.status_code == 200:
                    res_data = response.json()
                    ai_response = res_data['choices'][0]['message']['content']
                    return JsonResponse({'response': ai_response})
                else:
                    logger.error(f"DeepSeek API Error ({response.status_code}): {response.text}")
                    
                    if response.status_code == 429:
                        return JsonResponse({'response': _('Превышена квота запросов к DeepSeek AI. Пожалуйста, подождите немного.')})
                    
                    return JsonResponse({'response': _('Ошибка DeepSeek API ({}).').format(response.status_code)})
            except Exception as e:
                logger.error(f"AI Request Exception: {e}")
                # Fallback to local mode on connection error
        
        # --- ЛОКАЛЬНЫЙ РЕЖИМ (если API недоступен или превышена квота) ---
        user_msg_lower = user_msg.lower()
        responses = {
            'osi': _('Модель OSI состоит из 7 уровней. В нашей лаборатории есть отличный визуализатор.'),
            'ip': _('IP-адресация — это основа маршрутизации. Используй наш IP-калькулятор.'),
            'лаба': _('У нас есть лабораторные работы по OSI, IP, коммутации и маршрутизации.'),
            'привет': _('Привет! Я твой помощник Computer Networks. Чем могу помочь?'),
            'конструктор': _('В Сетевом конструкторе ты можешь создавать свои топологии.'),
            'автор': _('Автор проекта — Инкар Болатовна.'),
        }

        response_text = ""
        for key in responses:
            if key in user_msg_lower:
                response_text = responses[key]
                break
        
        if not response_text:
            response_text = _('Я временно работаю в ограниченном режиме из-за нагрузки на API DeepSeek. Пожалуйста, попробуй позже для более детального ответа или изучи материалы курса.')

        return JsonResponse({'response': response_text})
        
    except Exception as e:
        logger.exception("Hybrid AI Exception")
        return JsonResponse({'response': _('Произошла системная ошибка. Попробуйте позже.')}, status=200)
