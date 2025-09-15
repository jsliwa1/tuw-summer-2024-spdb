from django import forms
from .models import TextEntry

class TextEntryForm(forms.ModelForm):
    class Meta:
        model = TextEntry
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 1}),
        }
