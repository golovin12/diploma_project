import math, cmath
import uuid

import numpy as np
import matplotlib.pyplot as plt
from commpy.channels import awgn
from numba import jit

from modulation_script import QAMModem, PSKModem


def convert_base(num, to_base=2, from_base=2):
    # Функция для перевода из одной системы счисления в другую.
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]


# ФУНКЦИИ ДЛЯ ТЕСТА


# Функция принимает список вопросов с ответами, перемешивает вопросы
# Выводит пользователю запрашиваемое количество вопросов и отдельно ответы к ним
def vibor(spisok, kolich):
    import random
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


# Функция для чтения файла и последующего вывода заголовка, списка вопросов и отдельо ответов к ним
def for_test(file_name, kolich):
    vopr, otveti = [], []
    with open(file_name, 'r', encoding='UTF-8') as f:  # Читаю файл с вопросами
        zagolovok = f.readline()  # Извлекаю первую строку (заголовок вопросника) из файла
        while True:
            v = []
            for i in range(
                    7):  # Из файла извлекаю наборы вопросов (Вопрос, 4 варианта ответов, путь к рисунку, правльный ответ)
                v.append(f.readline())
            f.readline()
            if v[0] == '' or v[0] == '\n':  # Когда заканчиваются вопросы, останавливаю цикл
                break
            else:
                vopr.append(v)  # Если вопросы не закончились, то добавляю полученный набор в общий список вопросов
        voprosi, otveti = vibor(vopr, kolich)  # Отправляю блоки вопросов для перемешивания
    return zagolovok, voprosi, otveti  # Вывожу заголовок, Вопросы и ответы (индексы Вопросов совпадают с индексами ответов к этим вопросам)


# ФУНКИИ ДЛЯ ПРАКТИЧЕСКОЙ ЧАСТИ
# Построение графиков области решений и вывод пути для них
def graf(modem, modulation: str, modulation_position: int):
    b = "static/detect/graph/" + modulation + ".png"
    fig, ax = plt.subplots()
    modem.plot_constellation(modulation_position)
    if modulation_position == 2:
        plt.scatter(-1, 1, c='white', s=1)
        plt.scatter(1, -1, c='white', s=1)
    ax.set_xlabel('I (Синфазная ось)', labelpad=120)
    ax.set_ylabel('Q (Квадратурная ось)', labelpad=160)
    ax.spines['left'].set_position(('data', 0.0))
    ax.spines['bottom'].set_position(('data', 0.0))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    plt.title(modulation + " модуляция")
    plt.savefig(b)
    plt.close()
    return b


# Функция для ускорения расчёта процента
@jit(nopython=True)
def soobhenie(c, t_modulat):
    soobh = []
    for i in range(c):
        k = np.log2(t_modulat)
        if k == 1:
            for j in range(8):
                soobh.append(np.random.randint(0, 2, 1)[0])
        elif k == 2:
            for j in range(10):
                soobh.append(np.random.randint(0, 2, 1)[0])
        elif k == 3:
            for j in range(12):
                soobh.append(np.random.randint(0, 2, 1)[0])
        elif k == 4:
            for j in range(16):
                soobh.append(np.random.randint(0, 2, 1)[0])
        elif k == 5:
            for j in range(20):
                soobh.append(np.random.randint(0, 2, 1)[0])
        elif k == 6:
            for j in range(24):
                soobh.append(np.random.randint(0, 2, 1)[0])
        elif k == 7:
            for j in range(28):
                soobh.append(np.random.randint(0, 2, 1)[0])
        else:
            for j in range(32):
                soobh.append(np.random.randint(0, 2, 1)[0])
        return soobh


# Функция для ускорения расчёта процента
@jit(nopython=True)
def dem(demodulated):
    d = []
    for i in demodulated:
        d.append(i)
    return d


# Генерация сигнала, модулированного сигнала, сигнала, подверженного гауссовскому шуму и детектированного сигнала
def for_percent(c, modem, t_modulat, snr):
    n = int(t_modulat)
    soobh = soobhenie(c, n)
    modulated = modem.modulate(soobh)
    t = awgn(modulated, snr)
    demodulated = modem.demodulate(t, 'hard')
    d = dem(demodulated)
    if c == 10:
        if d == soobh:
            return "y"
        else:
            return "n"
    else:
        return soobh, d, modulated, t


# Построение графика модулированного сигнала и сигнала, пропущенного через шум; вывод пути до построенных графиков
def for_lab1(a, folder):
    vih = []
    for signal in a:
        fig, ax = plt.subplots()
        mr = 0
        for i in range(len(signal)):
            element = signal[i]
            g = np.linspace(mr, mr + 8 * math.pi, 200)
            mr += 8 * math.pi
            cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
            fas = cmath.phase(element)
            u = cel * np.sin(g + fas)
            if i + 1 < len(signal):
                plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
                    (signal[i + 1].real) ** 2 + (signal[i + 1].imag) ** 2) * np.sin(
                    cmath.phase(signal[i + 1]))], color='k')
            plt.plot(g, u)
        plt.grid()
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, В')
        file_name = uuid.uuid4()
        plt.savefig(f"detect/static/detect/{folder}/{file_name}.png")
        plt.close()
        vih.append(file_name)
    return vih


def for_lab2(a, folder):
    vih = []
    for signal in a:
        fig, ax = plt.subplots()
        mr = 0
        for i in range(len(signal)):
            element = signal[i]
            g = np.linspace(mr, mr + 8 * math.pi, 200)
            mr += 8 * math.pi
            cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
            fas = cmath.phase(element)
            u = cel * np.sin(g + fas)
            if i + 1 < len(signal):
                plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
                    (signal[i + 1].real) ** 2 + (signal[i + 1].imag) ** 2) * np.sin(
                    cmath.phase(signal[i + 1]))], color='k')
            plt.plot(g, u)
        file_name = uuid.uuid4()
        plt.grid()
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, В')
        plt.savefig(f"detect/static/detect/{folder}/{file_name}.png")
        plt.close()
        vih.append(file_name)
    return vih


def sozvezd(soobh, t_modulat, modulat, folder):
    vih = []
    fig, ax = plt.subplots()
    g = int(t_modulat)
    if modulat == "PSK":
        modem = PSKModem(g)
        m = "PSK модуляция"
    else:
        modem = QAMModem(g)
        m = "QAM модуляция"
    modem.plot_constellation(int(t_modulat))
    if int(t_modulat) == 2:
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
    ax.axes.get_xaxis().set_ticklabels([])
    ax.axes.get_yaxis().set_ticklabels([])
    plt.title(str(t_modulat) + "-" + m)
    for j in soobh:
        plt.scatter(j.real, j.imag)
    file_name = f"{uuid.uuid4()}-sozvezd"
    plt.savefig(f"detect/static/detect/{folder}/{file_name}.png")
    plt.close()
    vih.append(file_name)
    return vih
