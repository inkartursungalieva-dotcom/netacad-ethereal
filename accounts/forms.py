# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Форма регистрации с кастомными полями"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-12 pr-4 input-focus placeholder:text-outline',
            'placeholder': 'example@netacad.com',
            'id': 'id_email'
        })
    )
    
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-12 pr-12 input-focus placeholder:text-outline',
            'placeholder': '••••••••',
            'id': 'id_password1',
            'minlength': '8'
        })
    )
    
    password2 = forms.CharField(
        label=_('Подтвердите пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-12 pr-4 input-focus placeholder:text-outline',
            'placeholder': '••••••••',
            'id': 'id_password2'
        })
    )
    
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': _('Необходимо принять условия')},
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-outline-variant text-primary focus:ring-primary',
            'id': 'id_terms'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'language')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-12 pr-4 input-focus placeholder:text-outline',
                'placeholder': 'username',
                'id': 'id_username'
            }),
            'role': forms.HiddenInput(),
            'language': forms.HiddenInput(attrs={'value': 'ru'}),
        }
    
    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Этот email уже зарегистрирован'))
        return email
    
    def clean_terms(self):
        """Валидация согласия с условиями"""
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise ValidationError(_('Необходимо принять условия обслуживания'))
        return terms
    
    def save(self, commit=True):
        """Сохранение пользователя"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        role = self.cleaned_data.get('role')
        if role and role in dict(User.ROLE_CHOICES):
            user.role = role
        
        user.language = self.cleaned_data.get('language', 'ru')
        
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    
    first_name = forms.CharField(
        label=_('Имя'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-4 pr-4 input-focus placeholder:text-outline',
            'placeholder': _('Имя')
        })
    )
    
    last_name = forms.CharField(
        label=_('Фамилия'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-4 pr-4 input-focus placeholder:text-outline',
            'placeholder': _('Фамилия')
        })
    )
    
    bio = forms.CharField(
        label=_('О себе'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-surface-container-low border-none rounded-xl py-4 pl-4 pr-4 input-focus placeholder:text-outline',
            'placeholder': _('О себе'),
            'rows': 3
        })
    )
    
    avatar = forms.ImageField(
        label=_('Аватар'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'id_avatar'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'avatar')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError(_('Этот email уже используется.'))
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """
    Форма входа по EMAIL.
    
    ВАЖНО:
    - Поле называется 'username' (требование Django AuthenticationForm)
    - Но принимает email от пользователя
    - В clean_username() конвертируем email → username
    - В HTML у input должен быть name="username"
    """
    
    # 🔑 Поле называется username для совместимости с Django!
    username = forms.CharField(
        label=_('Электронная почта'),
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-5 py-4 bg-surface-container-low border-0 rounded-xl input-focus placeholder:text-outline-variant text-on-surface',
            'placeholder': 'example@netacad.kz',
            'id': 'id_email',
            'autocomplete': 'email',
            # ❌ НЕ добавляй 'name': 'email' — это ломает форму!
            # ✅ Django сам подставит name="username"
        })
    )
    
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-5 py-4 bg-surface-container-low border-0 rounded-xl input-focus placeholder:text-outline-variant text-on-surface',
            'placeholder': '••••••••',
            'id': 'id_password',
            'autocomplete': 'current-password'
        })
    )
    
    error_messages = {
        'invalid_login': _("Неверный email или пароль."),
        'inactive': _("Этот аккаунт не активен."),
    }
    
    def clean_username(self):
        """
        Принимаем email от пользователя, находим по нему пользователя,
        и возвращаем его username для аутентификации.
        """
        email = self.cleaned_data.get('username')  # Да, это email, но поле называется username
        
        if email:
            try:
                # Ищем пользователя по email (регистронезависимо)
                user = User.objects.get(email__iexact=email)
                # Возвращаем его username — Django будет аутентифицировать по нему
                return user.username
            except User.DoesNotExist:
                # Если пользователь не найден — вернём email как есть
                # (аутентификация всё равно не пройдёт, но ошибка будет корректной)
                pass
        return email
    
    def clean(self):
        """
        Основная валидация: проверяем пароль для найденного пользователя.
        """
        username = self.cleaned_data.get('username')  # Это уже username (из clean_username) или email
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Сначала пробуем стандартную аутентификацию Django
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                # Если не вышло — пробуем найти по email и проверить пароль напрямую
                # (на случай, если clean_username не сработал как ожидалось)
                try:
                    user = User.objects.get(email__iexact=username)
                    if user.check_password(password):
                        self.user_cache = user
                    else:
                        raise ValidationError(
                            self.error_messages['invalid_login'],
                            code='invalid_login',
                        )
                except User.DoesNotExist:
                    raise ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                    )
            else:
                # Если аутентификация прошла — проверяем, активен ли пользователь
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data
    
    def get_user(self):
        """Возвращает аутентифицированного пользователя."""
        return getattr(self, 'user_cache', None)