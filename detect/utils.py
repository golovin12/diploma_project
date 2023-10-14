import io
import math, cmath
import random

import numpy as np
import matplotlib.pyplot as plt
from commpy.channels import awgn

from modulation_script import Modem


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
