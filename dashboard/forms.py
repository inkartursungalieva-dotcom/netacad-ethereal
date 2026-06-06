from django import forms
from django.utils.translation import gettext_lazy as _
from courses.models import Module, Question, Choice
from laboratory.models import Lab
from django.forms import inlineformset_factory

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'description', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-outline-variant text-primary focus:ring-primary'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['module', 'text', 'hint', 'difficulty', 'category', 'type']
        widgets = {
            'module': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'text': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'rows': 3}),
            'hint': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'rows': 2}),
            'difficulty': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct', 'order', 'pair_text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'pair_text': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary'}),
        }

ChoiceFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm,
    extra=4, can_delete=True
)

class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['module', 'title', 'description', 'hints', 'scenario_data']
        widgets = {
            'module': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'rows': 4}),
            'hints': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'rows': 3}),
            'scenario_data': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface-container-lowest font-mono text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'rows': 10}),
        }
