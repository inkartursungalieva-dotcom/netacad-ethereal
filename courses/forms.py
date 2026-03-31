from django import forms
from .models import Resource
from django.utils.translation import gettext_lazy as _

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file', 'resource_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none',
                'placeholder': _('Введите название материала...')
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none',
                'placeholder': _('Краткое описание содержимого...'),
                'rows': 4
            }),
            'resource_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none cursor-pointer'
            }),
            'file': forms.FileInput(attrs={
                'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer',
                'id': 'resource-file-input'
            })
        }
