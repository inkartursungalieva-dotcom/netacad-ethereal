import os
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, **kwargs):
        # Если allauth не может найти SocialApp в базе, попробуем вернуть динамически
        try:
            # Используем kwargs напрямую, чтобы избежать дублирования аргументов (client_id, config и т.д.)
            app = super().get_app(request, provider=provider, **kwargs)
            logger.info(f"Successfully found SocialApp in DB for provider {provider}")
            return app
        except Exception as e:
            logger.warning(f"SocialApp not found in DB for {provider}, error: {e}. Trying env variables.")
            client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
            
            # Проверка: если в env хэш коммита, игнорируем его
            is_valid_google_id = client_id and client_id.endswith('.apps.googleusercontent.com')
            
            if provider == 'google' and is_valid_google_id:
                logger.info(f"Creating dynamic SocialApp for {provider} using env variables.")
                from allauth.socialaccount.models import SocialApp
                return SocialApp(
                    provider=provider,
                    name='Google',
                    client_id=client_id,
                    secret=client_secret
                )
            
            logger.error(f"Failed to find or create SocialApp for {provider}. ENV GOOGLE_CLIENT_ID length: {len(client_id) if client_id else 0}")
            raise
