from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
import json
import httpx
import os
import logging
from .ai_fallback import AIFallbackKnowledge
from .models import AIConversation, AIMessage
# from django_ratelimit.decorators import ratelimit  # Временно закомментировано 
from django.contrib.auth.decorators import login_required

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

# @ratelimit(key='ip', rate='12/m', method='POST')  # Временно закомментировано - использует session-based rate limiting
def ai_chat_api(request):
    """
    Гибридный ИИ: API DeepSeek с локальным отказоустойчивым режимом и сохранением истории диалогов.
    
    Использует синхронный режим для совместимости с WSGI (Gunicorn).
    
    Обработка ошибок:
    - 401: Требуется авторизация
    - 405: Неверный HTTP метод
    - 429: Превышена квота API
    - 500/502/503: Ошибки сервера DeepSeek
    - timeout: Таймаут запроса
    - network: Ошибки сети
    """
    import logging
    logger.info('ai_chat_api called! User:', request.user, 'Method:', request.method)
    if request.method != 'POST':
        logger.warning(f"AI API: Invalid method {request.method} from user {request.user.id if request.user.is_authenticated else 'anonymous'}")
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # 1. Проверка авторизации (Critical 4)
    if not request.user.is_authenticated:
        logger.warning(f"AI API: Unauthorized access attempt")
        return JsonResponse({'error': _('Авторизуйтесь для использования ИИ-чата')}, status=401)
    
    # 2. Rate limiting через сессию (12 запросов в минуту)
    rate_limit_key = 'ai_chat_requests'
    requests_data = request.session.get(rate_limit_key, {'count': 0, 'reset_time': timezone.now().timestamp() + 60})
    
    # Сброс счётчика если прошла минута
    if timezone.now().timestamp() > requests_data['reset_time']:
        requests_data = {'count': 0, 'reset_time': timezone.now().timestamp() + 60}
    
    if requests_data['count'] >= 12:
        logger.info(f"AI API: Rate limit triggered for user {request.user.id}")
        return JsonResponse({'response': _('Вы отправляете запросы слишком часто. Пожалуйста, подождите.')})
    
    requests_data['count'] += 1
    request.session[rate_limit_key] = requests_data
    
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '')
        conversation_id = data.get('conversation_id', None)
        
        if not user_msg or not user_msg.strip():
            logger.warning(f"AI API: Empty message from user {request.user.id}")
            return JsonResponse({'response': _('Пожалуйста, введите ваш вопрос.')})
        
        # --- СОХРАНЕНИЕ ИСТОРИИ ДИАЛОГОВ ---
        if not conversation_id:
            # Создаём новый диалог
            conversation = AIConversation.objects.create(
                user=request.user,
                title=user_msg[:50] if len(user_msg) > 50 else user_msg
            )
        else:
            # Получаем существующий диалог
            try:
                conversation = AIConversation.objects.get(id=conversation_id, user=request.user)
            except AIConversation.DoesNotExist:
                # Если диалог не найден, создаём новый
                conversation = AIConversation.objects.create(
                    user=request.user,
                    title=user_msg[:50] if len(user_msg) > 50 else user_msg
                )
        
        # Сохраняем сообщение пользователя
        AIMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_msg
        )
        
        gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        logger.info(f"GEMINI_API_KEY exists: {bool(gemini_api_key)}")
        logger.info(f"GEMINI_API_KEY prefix: {gemini_api_key[:10] if gemini_api_key else 'None'}")
        ai_response = None
        system_prompt = (
            "Ты — Computer Networks AI, экспертный помощник обучающей платформы по компьютерным сетям. "
            "Твоя задача: помогать студентам и преподавателям. "
            "Ты знаешь про 13 модулей курса (введение, OSI, IP, маршрутизация, коммутация, безопасность, беспроводные сети, облака и т.д.), "
            "про сетевой конструктор, лабораторию OSI и IP-калькулятор. "
            "Отвечай вежливо, профессионально на русском или казахском языке. "
            "Если вопрос касается топологии сети, предложи использовать наш Сетевой конструктор."
        )

        # Собираем историю сообщений для контекста
        # Получаем все сообщения, кроме самого последнего, которое мы только что сохранили (user's new message)
        conversation_history = []
        messages = list(conversation.messages.all().order_by('timestamp'))

        for msg in messages[:-1]:  # exclude the last (current user) message
            conversation_history.append({"role": msg.role, "content": msg.content})

        # Пробуем только Gemini
        if gemini_api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
                
                # Форматируем сообщения для Gemini (правильный формат с system_instruction)
                gemini_messages = []
                
                for hist_msg in conversation_history:
                    role = "user" if hist_msg["role"] == "user" else "model"
                    gemini_messages.append({"role": role, "parts": [{"text": hist_msg["content"]}]})
                
                # Добавляем текущее сообщение пользователя
                gemini_messages.append({"role": "user", "parts": [{"text": user_msg}]})
                
                payload = {
                    "systemInstruction": {"role": "user", "parts": [{"text": system_prompt}]},
                    "contents": gemini_messages,
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 8192,
                    },
                    "safetySettings": [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                }
                
                headers = {'Content-Type': 'application/json'}
                
                with httpx.Client() as client:
                    response = client.post(url, headers=headers, json=payload, timeout=15.0)
                
                if response.status_code == 200:
                    res_data = response.json()
                    candidates = res_data.get('candidates', [])
                    if candidates:
                        candidate = candidates[0]
                        if 'content' in candidate:
                            parts = candidate['content'].get('parts', [])
                            if parts:
                                ai_response = parts[0].get('text')
                    logger.info(f"AI API: Successful response (Gemini) for user {request.user.id}")
                else:
                    error_detail = response.text[:300] if response.text else 'No details'
                    logger.error(f"Gemini API Error ({response.status_code}): {error_detail}")
                    # Instead of falling back immediately, send an error message to user
                    if response.status_code == 429:
                        ai_response = "Квота API Gemini превышена. Пожалуйста, подождите немного или используйте локальный режим!"
                    else:
                        ai_response = f"Ошибка при подключении к Gemini API (код {response.status_code})."
            except Exception as e:
                logger.error(f"AI API: Gemini error for user {request.user.id}: {e}")
                ai_response = f"Произошла ошибка при подключении к Gemini: {str(e)}"
        else:
            ai_response = "GEMINI_API_KEY не установлен в настройках!"
        
        # Если Gemini не дал ответа, используем локальный режим как последнее средство
        if not ai_response or ai_response.startswith("Ошибка") or ai_response.startswith("Квота"):
            logger.info(f"AI API: Using local fallback mode for user {request.user.id}")
            ai_response = AIFallbackKnowledge.get_response(user_msg)
        
        # Сохраняем ответ ИИ
        AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        return JsonResponse({'response': ai_response, 'conversation_id': conversation.id})
        
    except json.JSONDecodeError:
        logger.error(f"AI API: Invalid JSON from user {request.user.id}")
        return JsonResponse({'response': _('Ошибка обработки запроса. Попробуйте снова.')})
    except Exception as e:
        logger.exception(f"AI API: Critical exception for user {request.user.id}")
        return JsonResponse({'response': _('Произошла системная ошибка. Попробуйте позже.')}, status=200)


# ==================== ONBOARDING VIEWS ====================

@login_required
def onboarding_welcome(request):
    """Приветственный экран онбординга"""
    if request.user.completed_onboarding:
        return redirect('dashboard:index')
    return render(request, 'onboarding/welcome.html')

@login_required
def onboarding_guide(request):
    """Экран с руководством по курсу"""
    if request.user.completed_onboarding:
        return redirect('dashboard:index')
    return render(request, 'onboarding/guide.html')

@login_required
def onboarding_labs(request):
    """Экран с информацией о лабораториях"""
    if request.user.completed_onboarding:
        return redirect('dashboard:index')
    return render(request, 'onboarding/labs.html')

@login_required
def onboarding_ai_assistant(request):
    """Экран с информацией об ИИ-помощнике"""
    if request.user.completed_onboarding:
        return redirect('dashboard:index')
    return render(request, 'onboarding/ai_assistant.html')

@login_required
def onboarding_complete(request):
    """Завершение онбординга"""
    if request.method == 'POST':
        request.user.completed_onboarding = True
        request.user.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def onboarding_skip(request):
    """Пропуск онбординга"""
    if request.method == 'POST':
        request.user.completed_onboarding = True
        request.user.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
