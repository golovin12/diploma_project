from django import forms

from modulation_script import QAMModem, PSKModem, Modem
from .consts import modulation_choices
from .models import Student, Modulation, TemporaryImage
from .utils import get_signals, get_signal_image, get_modulation_graph


class DemodulateInfluenceSNRFrom(forms.Form):
    modulation = forms.ChoiceField(label='Тип манипуляции', choices=modulation_choices)
    snr = forms.DecimalField(label='SNR', initial=6, decimal_places=2, max_digits=4, min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['snr'].widget.attrs['placeholder'] = '12.55'
        self.fields['snr'].widget.attrs['class'] = 'is-invalid'

    @staticmethod
    def get_modulation_img_path(modem: Modem, modulation_position: int, modulation: str) -> str:
        """Путь до изображения сигнального созвездия для выбранного типа модуляции"""
        modulation_bd, create = Modulation.objects.get_or_create(method=modulation)
        if not modulation_bd.stars_image:
            content = get_modulation_graph(modem, modulation_position, modulation)
            modulation_bd.stars_image.save(f"{modulation}.png", content)
        return modulation_bd.stars_image.url

    @staticmethod
    def calculate_percent(modem: Modem, modulation_position: int, snr: float) -> float:
        """Расчёт процента ошибочно декодированных сообщений для данного типа модуляции и SNR"""
        success_demodulate = 0
        for i in range(1000):
            messages = get_signals(modem, modulation_position, snr)
            original_message, demodulated_message = messages[0], messages[1]
            if demodulated_message == original_message:
                success_demodulate += 1
        return round(100 - success_demodulate * 100 / 1000, 3)

    def get_context_data(self):
        snr = float(self.cleaned_data['snr'])
        modulation = self.cleaned_data['modulation']
        modulation_position, modulation_type = modulation.split('-')
        modulation_position = int(modulation_position)
        # Инициализация модема
        if modulation_type == "PSK":
            modem = PSKModem(modulation_position)
        else:
            modem = QAMModem(modulation_position)

        # Создание сигналов и сохранение изображений
        original_msg, demodulated_msg, modulated_signal, gaussian_signal = get_signals(modem, modulation_position, snr)
        modulated_signal_image = TemporaryImage.objects.create()
        modulated_signal_image.image.save(f'{modulation}{modulated_signal_image.id}.png',
                                          get_signal_image(modulated_signal))
        signal_with_gauss_image = TemporaryImage.objects.create()
        signal_with_gauss_image.image.save(f'{modulation}{signal_with_gauss_image.id}.png',
                                           get_signal_image(gaussian_signal))
        # Формирование вывода о влиянии SNR на выбранный тип модуляции
        percent_errors = self.calculate_percent(modem, modulation_position, snr)
        if 0 < percent_errors <= 1:
            is_complete = True
        else:
            is_complete = False

        return {'original_message': original_msg,
                'demodulated_message': demodulated_msg,
                'path_to_modulated_signal': modulated_signal_image.image.url,
                'path_to_signal_with_gauss': signal_with_gauss_image.image.url,
                'modulation_image_path': self.get_modulation_img_path(modem, modulation_position, modulation),
                'percent_errors': percent_errors,
                'is_complete': is_complete,
                'modulation': modulation,
                'snr': snr,
                }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('name', 'surname', 'group')

    def get_user(self):
        name = self.cleaned_data['name']
        surname = self.cleaned_data['surname']
        group = self.cleaned_data['group']
        student = Student.objects.filter(name__iexact=name, surname__iexact=surname, group__iexact=group).first()
        if student:
            return student
        return Student.objects.create(name=name.capitalize(), surname=surname.capitalize(), group=group.upper())
