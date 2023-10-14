import io
import math, cmath
import random
import uuid

import numpy as np
import matplotlib.pyplot as plt
from commpy.channels import awgn
from scipy.fft import fft, ifft

from detect.models import Student, StudentLab2, StudentLab3, StudentLab4
from modulation_script import Modem, PSKModem, QAMModem, OFDMModem


def convert_base(num, to_base=2, from_base=2):
    """Функция для перевода из одной системы счисления в другую."""
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]


def vibor(spisok, kolich):
    """
    Функция принимает список вопросов с ответами, перемешивает вопросы.
    Выводит пользователю запрашиваемое количество вопросов и отдельно ответы к ним
    """
    voprosi = []
    otveti = []
    random.shuffle(spisok)  # Перемешивает поступивший набов вопросов
    spisok = spisok[:kolich]  # Обрезает набор вопросов до нужного количества
    for i in spisok:
        # Перебирает каждый блок вопросов
        v = i[1:5]
        random.shuffle(v)  # Перемешивает варианты ответов на вопросы из блока
        v = i[:1] + v  # К самому вопросу добавляются перемешанные варианты ответов
        v.append(len(
            voprosi) + 1)  # К полученному списку добавляется номер вопроса (Этот номер задаётся в html-файле в "name")
        put = i[-1:]
        put = put[0][:-1]
        v.append(put)
        voprosi.append(v)  # Полученный вопрос добавляется в общий список вопросов
        o = i[-2:-1]  # Из изначалього блока достаётся Ответ
        o = o[0][:-1] + "\r\n"  # Преобразую ответ, чтобы его можно было сравнить
        otveti.append(o)  # Добавляю ответ к общему набору ответов
    return voprosi, otveti  # Выводится полученные наборы вопросов и ответов, при этом, индексы каждого вопроса совпадают с индексами ответов для этих вопросов


def for_test(file_name, kolich):
    """Функция для чтения файла и последующего вывода заголовка, списка вопросов и отдельно ответов к ним"""
    vopr, otveti = [], []
    with open(file_name, 'r', encoding='UTF-8') as f:  # Читаю файл с вопросами
        zagolovok = f.readline()  # Извлекаю первую строку (заголовок вопросника) из файла
        while True:
            v = []
            for i in range(7):
                # Из файла извлекаю наборы вопросов (Вопрос, 4 варианта ответов, путь к рисунку, правильный ответ)
                v.append(f.readline())
            f.readline()
            if v[0] == '' or v[0] == '\n':  # Когда заканчиваются вопросы, останавливаю цикл
                break
            else:
                vopr.append(v)  # Если вопросы не закончились, то добавляю полученный набор в общий список вопросов
    voprosi, otveti = vibor(vopr, kolich)  # Отправляю блоки вопросов для перемешивания
    # Вывожу заголовок, Вопросы и ответы (индексы Вопросов совпадают с индексами ответов к этим вопросам)
    return zagolovok, voprosi, otveti


def get_signal_stars(modem: Modem, modulation_position: int, modulation: str,
                     signal: np.ndarray[np.complex_] = None) -> io.BytesIO:
    """Построение сигнального созвездия"""
    fig, ax = plt.subplots()
    modem.plot_constellation(modulation_position)
    if modulation_position == 2:
        plt.scatter(-0.5, 0.5, c='white', s=1)
        plt.scatter(0.5, -0.5, c='white', s=1)
    ax.set_xlabel('I (Синфазная ось)', labelpad=120)
    ax.set_ylabel('Q (Квадратурная ось)', labelpad=160)
    ax.spines['left'].set_position(('data', 0.0))
    ax.spines['bottom'].set_position(('data', 0.0))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    plt.title(f"{modulation} модуляция")
    if signal is not None:
        ax.axes.get_xaxis().set_ticklabels([])
        ax.axes.get_yaxis().set_ticklabels([])
        for complex_number in signal:
            plt.scatter(complex_number.real, complex_number.imag)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return buf


def get_random_message(modulation_position: int):
    k = int(math.log2(modulation_position))
    return [random.choice((0, 1)) for i in range(k * 8)]


def get_signals(modem: Modem, modulation_position: int,
                snr: float) -> tuple[list, list, np.ndarray[np.complex_], np.ndarray[np.complex_]]:
    """
    Генерация сигнала, модулированного сигнала, сигнала, подверженного гауссовскому шуму и детектированного сигнала
    """
    original_message = get_random_message(modulation_position)
    modulated_signal = modem.modulate(original_message)
    gaussian_signal = awgn(modulated_signal, snr)
    demodulated_message = [i for i in modem.demodulate(gaussian_signal, 'hard')]
    return original_message, demodulated_message, modulated_signal, gaussian_signal


def get_modem_by_modulation(modulation_type: str, modulation_position: int) -> Modem:
    if modulation_type == "PSK":
        return PSKModem(modulation_position)
    return QAMModem(modulation_position)


def get_signal_image(signal: np.ndarray[np.complex_]) -> io.BytesIO:
    """Построение графиков сигналов"""
    fig, ax = plt.subplots()
    mr = 0
    for next_index, complex_number in enumerate(signal, start=1):
        g = np.linspace(mr, mr + 8 * math.pi, 200)
        mr += 8 * math.pi
        cel = math.sqrt(2) * math.sqrt(complex_number.real ** 2 + complex_number.imag ** 2)
        fas = cmath.phase(complex_number)
        u = cel * np.sin(g + fas)
        if next_index < len(signal):
            plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
                signal[next_index].real ** 2 + signal[next_index].imag ** 2) * np.sin(
                cmath.phase(signal[next_index]))], color='k')
        plt.plot(g, u)
    plt.grid()
    ax.set_xlabel('Время, с')
    ax.set_ylabel('Амплитуда, В')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return buf


def get_lab2_tasks_by_student(student: Student) -> list[StudentLab2]:
    lab2_tasks = []
    for modulation in ('4-PSK', '4-QAM', '16-QAM'):  # todo заменить на константы
        lab2, create = StudentLab2.objects.get_or_create(student=student, modulation=modulation)
        if not lab2.signal:
            modulation_position, modulation_type = modulation.split('-')
            modulation_position = int(modulation_position)
            modem = get_modem_by_modulation(modulation_type, modulation_position)
            message = get_random_message(modulation_position)
            signal_with_gaussian = awgn(modem.modulate(message), modulation_position + 11)
            lab2.signal = ''.join(str(i) for i in modem.demodulate(signal_with_gaussian, "hard"))
            signal_image = get_signal_image(signal_with_gaussian)
            lab2.signal_image.save(f'signal_{lab2.id}.png', signal_image)
            stars_image = get_signal_stars(modem, modulation_position, modulation, signal_with_gaussian)
            lab2.stars_image.save(f'stars_{lab2.id}.png', stars_image)
            lab2.save()
        lab2_tasks.append(lab2)
    return lab2_tasks


def get_lab3_tasks_by_student(student: Student) -> list[StudentLab3]:
    lab3_tasks = []
    modem = get_modem_by_modulation('PSK', 4)
    for multiplier in (1, 2, 3):
        lab3, create = StudentLab3.objects.get_or_create(student=student, multiplier=multiplier)
        if not lab3.signal:
            message = get_random_message(4 * multiplier)
            lab3.signal = ''.join(str(i) for i in message)
            lab3.signal_complex = [i for i in awgn(modem.modulate(message), 20)]
            lab3.save()
        lab3_tasks.append(lab3)
    return lab3_tasks


def get_lab4_by_student(student: Student) -> StudentLab4:
    lab4_task, create = StudentLab4.objects.get_or_create(student=student)
    if not lab4_task.signal:
        # Формирование сигнала и OFDM-модуляция
        message = [random.choice((0, 1)) for i in range(96)]
        modem = OFDMModem()
        modulated_signal = modem.modulate(message)
        signal_with_gaussian = awgn(modulated_signal, 30)
        demodulated_message = modem.demodulate(signal_with_gaussian)
        lab4_task.signal = "".join(str(i) for i in demodulated_message)
        lab4_task.signal_complex = [i for i in signal_with_gaussian]
        lab4_task.signal_image.save(f'ofdm_{lab4_task.id}.png', modem.get_signal_image(signal_with_gaussian))
        lab4_task.save()
    return lab4_task
