from django import forms

from .consts import modulation_choices


class ModulationInfluenceSNRFrom(forms.Form):
    modulation = forms.ChoiceField(label='Тип манипуляции', choices=modulation_choices)
    snr = forms.DecimalField(label='SNR', required=False)


class UserForm(forms.Form):
    name = forms.CharField(label="Имя", min_length=2, max_length=20)
    family = forms.CharField(label="Фамилия", min_length=3, max_length=20)
    group = forms.CharField(label="Группа", min_length=2, max_length=20)
