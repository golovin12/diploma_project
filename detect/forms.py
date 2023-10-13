from django import forms

from modulation_script import QAMModem, PSKModem
from .consts import modulation_choices
from .utils import for_percent, for_lab1


class DemodulateInfluenceSNRFrom(forms.Form):
    modulation = forms.ChoiceField(label='Тип манипуляции', choices=modulation_choices)
    snr = forms.DecimalField(label='SNR', initial=6, decimal_places=2, max_digits=5, min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['snr'].widget.attrs['placeholder'] = '12.55'
        self.fields['snr'].widget.attrs['class'] = 'is-invalid'
        self._path_to_modulation_img = None
        self._original_message = None
        self._demodulated_message = None
        self._path_to_orig_message = None
        self._path_to_message_with_gauss = None

    @property
    def original_message(self):
        return self._original_message

    @property
    def demodulated_message(self):
        return self._demodulated_message

    @property
    def path_to_modulation_img(self):
        return self._path_to_modulation_img

    @property
    def path_to_orig_message(self):
        return self._path_to_orig_message

    @property
    def path_to_message_with_gauss(self):
        return self._path_to_message_with_gauss

    def calculate_percent(self) -> float:
        """Эмулирует процесс демодуляции сообщений и возвращает процент успешно демодулированных сообщений из 1000"""
        # К юзеру привязывается лаба.
        # В этой лабе сохраняются картинки последних сигналов (старые - удаляются) !!!Для каждой модуляции!!!.
        # Если юзер прошёл лабу - ему предлагают выполнить с другой модуляцией или перейти к следующей лабе.
        modulation = self.cleaned_data['modulation']
        snr = float(self.cleaned_data['snr'])
        modulation_position, modulation_type = modulation.split('-')
        modulation_position = int(modulation_position)

        # Определить модем, построить графики,
        if modulation_type == "PSK":  # Создание модема
            modem = PSKModem(modulation_position)
        else:
            modem = QAMModem(modulation_position)
        # Получение переменных (сообщение, демодулированный список, модулированный список и сообщ после гауссовского шума)
        msg, d, modulated, t = for_percent(1, modem, modulation_position, snr)
        # Для данного типа модуляции и SNR расчёт процента ошибочно декодированных сообщений
        a = 0
        for i in range(1000):
            soobh = for_percent(10, modem, modulation_position, snr)
            if "y" == soobh:
                a += 1
        self._original_message = msg
        self._demodulated_message = d
        # Проверка на наличие графика области решений graf(modem, modulation, modulation_position)
        self._path_to_modulation_img = f"/static/detect/graph/{modulation}.png"
        # Создание сигналов и получение их номера в файле
        images = for_lab1([modulated, t], "lab1")
        self._path_to_orig_message = f"/static/detect/lab1/{images[0]}.png"
        self._path_to_message_with_gauss = f"/static/detect/lab1/{images[1]}.png"
        return round(100 - a * 100 / 1000, 3)


class UserForm(forms.Form):
    name = forms.CharField(label="Имя", min_length=2, max_length=20)
    family = forms.CharField(label="Фамилия", min_length=3, max_length=20)
    group = forms.CharField(label="Группа", min_length=2, max_length=20)
