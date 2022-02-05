import random
import warnings

import numpy
from commpy.channels import *
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from matplotlib import pyplot as plt
from numba import jit
from scipy.fft import fft
from scipy.fft import ifft

from modulation_script import *
from .formes import UserForm
from .models import Person

warnings.filterwarnings('ignore')

# Запоминает вопросы пользователя
otveti_for_users = []
otveti_slovar = {}
file_lab1 = []
file_lab2 = []
file_lab4 = []
file_sozvezd2 = []


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
# Функция принимает блок вопросов и ответов, сохраняет их под определённым id и отправляет этот id пользователю
def znach(voprosi, otveti):
    global otveti_slovar
    t = random.randint(-99999999, 99999999)
    while otveti_slovar.get(str(t)) != None:
        t = random.randint(-99999999, 99999999)
    otveti_slovar[str(t)] = [voprosi, otveti]
    return str(t)


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
def graf(modulat, t_modulat):
    b = "static/graph/" + t_modulat + modulat + ".png"
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
    plt.title(t_modulat + "-" + m)
    plt.savefig(b)
    plt.close()
    return b


# Функция для ускорения расчёта процента
@jit(nopython=True)
def soobhenie(c, t_modulat):
    soobh = []
    for i in range(c):
        k = numpy.log2(t_modulat)
        if k == 1:
            for j in range(8):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        elif k == 2:
            for j in range(10):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        elif k == 3:
            for j in range(12):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        elif k == 4:
            for j in range(16):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        elif k == 5:
            for j in range(20):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        elif k == 6:
            for j in range(24):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        elif k == 7:
            for j in range(28):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
        else:
            for j in range(32):
                soobh.append(numpy.random.randint(0, 2, 1)[0])
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
def for_lab1(a, put):
    import math, cmath
    import numpy as np
    global file_lab1
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
        if len(file_lab1) >= 104:
            file_lab1 = []
        a = str(len(file_lab1))
        file_lab1.append(a)
        plt.grid()
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, В')
        plt.savefig("static/" + put + "/" + file_lab1[-1:][0] + ".png")
        plt.close()
        vih.append(a)
    return vih


def for_lab2(a, put):
    import math, cmath
    import numpy as np
    global file_lab2
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
        if len(file_lab2) >= 52:
            file_lab2 = []
        a = str(len(file_lab2))
        file_lab2.append(a)
        plt.grid()
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, В')
        plt.savefig("static/" + put + "/" + file_lab2[-1:][0] + ".png")
        plt.close()
        vih.append(a)
    return vih


def sozvezd(soobh, t_modulat, modulat, put):
    global file_sozvezd2
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
    if len(file_sozvezd2) >= 52:
        file_sozvezd2 = []
    a = str(len(file_sozvezd2))
    file_sozvezd2.append(a)
    plt.savefig("static/" + put + "/" + file_sozvezd2[-1:][0] + "sozvezd.png")
    plt.close()
    vih.append(a)
    return vih


# Выводит главную страницу
def glavnaya(request):
    with open('theory/glavn.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    glavn = []
    for i in lines:
        glavn.append(i[:-1])
    data = {"zagolovok": "Лабораторная работа на тему 'Детектирование сигналов в современных системах связи'",
            "lines": glavn
            }
    return render(request, 'blog/glavnaya.html', context=data)


# Выводит теорию из файла
def theory1(request):
    with open('theory/theory1.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    data = {"tema": "1. Общие сведения о задаче детектирования",
            "lines": lines
            }
    return render(request, 'blog/theory1.html', context=data)


# Выводит теорию из файла
def theory2(request):
    with open('theory/theory2.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    data = {"tema": "2. Классификация методов детектирования",
            "lines": lines
            }
    return render(request, 'blog/theory2.html', context=data)


# Выводит теорию из файла
def theory3(request):
    with open('theory/theory3.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    data = {"tema": "3. Перспективы развития методов детектирования",
            "lines": lines
            }
    return render(request, 'blog/theory3.html', context=data)


# Оформление шаблона
def shablon(request):
    return render(request, 'blog/shablon.html')


# Для практических заданий
@never_cache
def laborathory1(request):
    global file_lab1
    # Создание графика
    if request.method == "POST":
        prin = request.POST.get("Modulation")  # Получаю тип модуляции, выбранный пользователем
        snr = float(request.POST.get("snr"))  # Получаю SNR выбранное пользователем
        modulat = prin[-3:]
        t_modulat = prin[:-3]
        graf(modulat, t_modulat)  # Проверка на наличие графика области решений
        if modulat == "PSK":  # Создание модема
            modem = PSKModem(int(t_modulat))
        else:
            modem = QAMModem(int(t_modulat))
        msg, d, modulated, t = for_percent(1, modem, t_modulat,
                                           snr)  # Получение переменных (сообщение, демодулированный список, модулированный список и сообщ после гауссовского шума)
        f1, f2 = for_lab1([modulated, t], "lab1")[0], for_lab1([modulated, t], "lab1")[
            1]  # Создание сигналов и получение их номера в файле
        # Для данного типа модуляции и SNR расчёт процента ошибочно принятых сообщений
        a = 0
        for i in range(1000):
            soobh = for_percent(10, modem, t_modulat, snr)
            if "y" == soobh:
                a += 1
            else:
                a = a
        percent = round(100 - a * 100 / 1000, 3)
        # Формирование вывода о данном типе модуляции и SNR
        c = ""
        if percent <= 1 and percent != 0:
            c = "0"
            itog = "Вы справились с заданием, вы подобрали такое SNR, при котором при детектирвоании 1000 сообщений, с ошибкой было детектировано всего {}%, что соответствует условию 'около 0.5%'. Зафиксируйте полученный результат".format(
                percent)
        elif percent == 0:
            c = "1"
            itog = "Продолжайте подбирать SNR (уменьшайте значение). Из 1000 переданных сообщений, с ошибкой было детектировано {}%, а вам необходимо подобрать такое SNR, при котором вероятность детектирования сообщения с ошибкой будет 'около 0.5%'".format(
                percent)
        else:
            c = "1"
            itog = "Продолжайте подбирать SNR (увеличивайте значение). Из 1000 переданных сообщений, с ошибкой было детектировано целых {}%, а это больше необходимых 0.5%".format(
                percent)
        return render(request, 'blog/laborathory1.html',
                      context={"modulat": modulat, "t_modulat": t_modulat, "msg": msg, "c": c,
                               "demodulated": d, "itog": itog, "f1": f1, "f2": f2, "snr": snr})
    else:
        return render(request, 'blog/vhod.html')


@never_cache
def laborathory2(request):
    global file_lab2, file_sozvezd2
    if request.method == "POST":
        prov1 = convert_base(request.POST.get("prov1"), 2, 17)
        prov1 = prov1[::-1][3:][:-3]
        prov2 = convert_base(request.POST.get("prov2"), 2, 28)
        prov2 = prov2[::-1][3:][:-3]
        prov3 = convert_base(request.POST.get("prov3"), 2, 23)
        prov3 = prov3[::-1][3:][:-3]
        otv1 = request.POST.get("otv1")
        otv2 = request.POST.get("otv2")
        otv3 = request.POST.get("otv3")
        c = 0
        for i in [prov1, prov2, prov3]:
            if i in [otv1, otv2, otv3]:
                c += 1
        if c == 3:
            result = "Вы успешно справились с заданием 2. Покажите результат преподавателю!"
        else:
            result = "Вы не справились с заданием, попробуйте ещё раз! Вы правильно детектировали {} сигналов.".format(
                c)
        return render(request, 'blog/result.html', context={"result": result})
    else:
        d = []
        vih = []
        put_sozv = []
        modems = [PSKModem(4), QAMModem(4), QAMModem(16)]
        prim = PSKModem(2)
        prim_sig = [0, 1, 1, 0, 1, 0, 0, 0, 1]
        prim_vih = awgn(prim.modulate(prim_sig), 13)
        vih.append(prim_vih)
        d.append(prim.demodulate(prim_vih, "hard"))
        for i in modems:
            if i in modems[:-1]:
                snr = 15
            else:
                snr = 21
            if snr == 15:
                a = random.choice(range(16, 20, 2))
            else:
                a = random.choice(range(32, 40, 4))
            msg = []
            for j in range(a):
                msg.append(random.choice([0, 1]))
            t = awgn(i.modulate(msg), snr)
            vih.append(t)
            d.append(i.demodulate(t, "hard"))
        t_modulat = [2, 4, 4, 16]
        modulat = ["PSK", "PSK", "QAM", "QAM"]
        for i in range(len(vih)):
            put_sozv.append(sozvezd(vih[i], t_modulat[i], modulat[i], "lab2"))
        vih_put = for_lab2(vih, "lab2")
        det = []
        for i in d:
            bd = ""
            for j in i:
                bd += str(j)
            det.append(bd)
        m1 = "101" + det[1][::-1] + "101"
        det[1] = convert_base(m1, 17, 2)
        m2 = "110" + det[2][::-1] + "011"
        det[2] = convert_base(m2, 28, 2)
        m3 = "100" + det[3][::-1] + "001"
        det[3] = convert_base(m3, 23, 2)
        return render(request, 'blog/laborathory2.html', context={"d": det, "vih_put": vih_put, "put_sozv": put_sozv})


@never_cache
def laborathory3(request):
    if request.method == "POST":
        mess1 = convert_base(request.POST.get("mess1"), 2, 21)
        mess1 = mess1[::-1][7:][:-6]
        mess2 = convert_base(request.POST.get("mess2"), 2, 24)
        mess2 = mess2[::-1][7:][:-6]
        mess3 = convert_base(request.POST.get("mess3"), 2, 22)
        mess3 = mess3[::-1][7:][:-6]
        otv1 = request.POST.get("otv1")
        otv2 = request.POST.get("otv2")
        otv3 = request.POST.get("otv3")
        c = 0
        for i in [mess1, mess2, mess3]:
            if i in [otv1, otv2, otv3]:
                c += 1
        if c == 3:
            result = "Вы успешно справились с заданием 3. Покажите результат преподавателю!"
        else:
            result = "Вы не справились с заданием, попробуйте ещё раз! Вы правильно детектировали {} сигналов.".format(
                c)
        return render(request, 'blog/result.html', context={"result": result})
    else:
        # Формирование 3 сигналов для проверки детектора.
        modem = PSKModem(4)
        c = 1
        mess = []
        for i in range(3):
            d = ""
            c = c * 2
            for k in range(c * 10):
                d += random.choice(["0", "1"])
            a = ""
            b = ""
            for o in range(5):
                a += random.choice(["0", "1"])
            for o in range(6):
                b += random.choice(["0", "1"])
            d = "1" + a + d[::-1] + b + "1"
            mess.append(d)
        for_modulat = []
        for i in mess:
            pok = i[::-1][7:][:-6]
            vih = []
            for k in pok:
                vih.append(int(k))
            for_modulat.append(vih)
        spisok = []
        for i in for_modulat:
            c = awgn(modem.modulate(i), 20)
            otpr = []
            for l in c:
                otpr.append(l)
            spisok.append(otpr)
        mess[0] = convert_base(mess[0], 21, 2)
        mess[1] = convert_base(mess[1], 24, 2)
        mess[2] = convert_base(mess[2], 22, 2)
        return render(request, 'blog/laborathory3.html', context={"spisok": spisok, "mess": mess})


@never_cache
def laborathory4(request):
    global file_lab4
    if request.method == "POST":
        vihod = request.POST.get("vihod")
        vihod = convert_base(vihod, 2, 20)[::-1][3:][:-3]
        otv = request.POST.get("otv")
        if otv == vihod:
            result = "Вы успешно выполнили задание 4. Покажите результат преподавателю."
        else:
            result = "Вы не справились с 4 заданием, попробуйте ещё раз."
        return render(request, 'blog/result.html', context={"result": result})
    else:
        # Формирование сигнала и OFDM-модуляция
        msg = []
        for i in range(100):
            msg.append(random.choice([0, 1]))
        modem1 = PSKModem(4)
        msg1 = []
        msg2 = []
        msg3 = []
        msg4 = []
        for i in range(0, len(msg), 4):
            msg1.append(msg[i])
            msg2.append(msg[i + 1])
            msg3.append(msg[i + 2])
            msg4.append(msg[i + 3])
        mod1 = modem1.modulate(msg1)
        ofmod1 = ifft(mod1)
        mod2 = modem1.modulate(msg2)
        ofmod2 = ifft(mod2)
        mod3 = modem1.modulate(msg3)
        ofmod3 = ifft(mod3)
        mod4 = modem1.modulate(msg4)
        ofmod4 = ifft(mod4)
        ofperedach = []
        for i in range(len(ofmod1)):
            ofperedach.append(ofmod1[i])
            ofperedach.append(ofmod2[i])
            ofperedach.append(ofmod3[i])
            ofperedach.append(ofmod4[i])
        of_for_priem = awgn(ofperedach, 30)
        signal = []
        for i in of_for_priem:
            signal.append(i)
        if len(file_lab4) <= 50:
            put = str(len(file_lab4))
            file_lab4.append(put)
        else:
            file_lab4 = []
            put = str(len(file_lab4))
            file_lab4.append(put)
        plt.plot(of_for_priem)
        plt.grid()
        plt.savefig("static/lab4/" + put + ".png")
        plt.close()
        # OFDM-демодуляция
        for_demod1 = []
        for_demod2 = []
        for_demod3 = []
        for_demod4 = []
        for i in range(0, int(len(of_for_priem)), 4):
            for_demod1.append(of_for_priem[i])
            for_demod2.append(of_for_priem[i + 1])
            for_demod3.append(of_for_priem[i + 2])
            for_demod4.append(of_for_priem[i + 3])
        demod1 = modem1.demodulate(fft(for_demod1), "hard")
        demod2 = modem1.demodulate(fft(for_demod2), "hard")
        demod3 = modem1.demodulate(fft(for_demod3), "hard")
        demod4 = modem1.demodulate(fft(for_demod4), "hard")
        sig_vih = []
        for i in range(len(demod1)):
            sig_vih.append(demod1[i])
            sig_vih.append(demod2[i])
            sig_vih.append(demod3[i])
            sig_vih.append(demod4[i])
        vihod = ""
        for i in sig_vih:
            vihod += str(i)
        vihod = "101" + vihod[::-1] + "011"
        vihod = convert_base(vihod, 20, 2)
        return render(request, 'blog/laborathory4.html', context={"put": put, "signal": signal, "vihod": vihod})


@never_cache
def result_is_db(request):
    a = Person.objects.all()
    spisok = []
    for i in range(len(a)):
        obj = ""
        some_person = a[i]
        obj += str(i + 1) + ") " + some_person.name
        obj += " " + some_person.family
        obj += " из группы " + some_person.group
        obj += " прошёл тест на " + str(some_person.percent) + "% "
        obj += "(время прохождения: " + str(some_person.created_date)[:19] + ")"
        spisok.append(obj)
    spisok_vih = spisok[::-1][:50]
    return render(request, 'blog/result_is_db.html', context={"spisok": spisok_vih})


# Выводит Тестовые вопросы, просит пользователя авторизоваться и, при успешном выполнении теста, выводит результат.
@never_cache
def tests(request):
    global otveti_for_users
    c = 0
    userform = UserForm()  # Создаются поля для ввода Имени, Фамилии и Группы
    if request.method == "POST":  # Проверяется, вводил ли пользователь свои данные и ответил ли на вопросы
        # Т.к. изначально при входе на страницу ничего не введено, то эта функция вызывается после else (поэтому сначала надо смотреть на работу этого пункта)
        name = request.POST.get("name")
        family = request.POST.get("family")
        group = request.POST.get("group")
        id = request.POST.get("id")
        voprosi, otveti = otveti_slovar.get(id)[0], otveti_slovar.get(id)[1]
        for i in range(len(voprosi)):  # Перебирает каждый ответ, выбранный пользователем
            a = request.POST.get(
                str(voprosi[i][5]))  # Извлекаю из каждого вопроса варианты ответов, выбранные пользователем
            if a == otveti[i]:  # Сверяю извлеченный ответ с правильным ответом
                c += 1
        percent = 100 * c // len(voprosi)  # Подсчёт процента правильных ответов пользователя
        # Удаление лишних записей из базы данных
        if Person.objects.count() > 100:
            while Person.objects.count() > 50:
                g = Person.objects.values_list("id").first()[0]
                Person.objects.filter(id=g).delete()
        # Удаление из памяти лишних блоков Вопросы/ответы
        if len(otveti_for_users) >= 100:
            otveti_for_users.remove(id)
            otveti_slovar.pop(id)
            while len(otveti_for_users) > 50:
                p = otveti_for_users.pop(0)
                otveti_slovar.pop(p)
        if percent >= 80:  # Если процент больше 80, то создаю в БД строку, в которой записываются Данные пользователя и процент правильных ответов,
            # а также отправляет пользователя на страницу, где будет написан результат выполнения теста
            Person.objects.create(name=name, family=family, group=group, percent=percent)
            otveti_for_users.remove(id)
            otveti_slovar.pop(id)
            result = "{0} {1} из группы {2}. Вы прошли тест на: {3}%. Покажите результат преподавателю!".format(name,
                                                                                                                family,
                                                                                                                group,
                                                                                                                percent)
            return render(request, 'blog/result.html', context={"result": result})
        else:  # Если процент выполнения меньше 80, то заново формируются блоки вопросов и ответов, пользователь отправляется заново проходить тест
            zagolovok, voprosi, otveti = for_test('tests/test1.txt', 15)
            otveti_for_users.remove(id)
            otveti_slovar.pop(id)
            id = znach(voprosi, otveti)
            otveti_for_users.append(id)
            result = "Вы прошли тест на: {}%. Попробуйте ещё раз!".format(percent)
            return render(request, 'blog/tests.html',
                          context={"zagolovok": zagolovok, "voprosi": voprosi, "form": userform, "result": result,
                                   "id": id})
    else:  # Когда пользователь только заходит на страницу теста, то для него формируются вопросы и ответы, которые запоминаются в функции func5
        zagolovok, voprosi, otveti = for_test('tests/test1.txt',
                                              15)  # Получение из файла перемешанных вопросов и ответов к ним.
        id = znach(voprosi, otveti)
        otveti_for_users.append(id)
        result = "Введите свои данные и проходите тест:"
        return render(request, 'blog/tests.html',
                      context={"zagolovok": zagolovok, "voprosi": voprosi, "form": userform, "result": result,
                               "id": id})


# Обработчик ошибок
def m304(request):
    return render(request, 'blog/304.html')


def m400(request, exception):
    return render(request, 'blog/400.html')


def m403(request, exception):
    return render(request, 'blog/403.html')


def m404(request, exception):
    return render(request, 'blog/404.html')


def m405(request):
    return render(request, 'blog/405.html')


def m410(request):
    return render(request, 'blog/410.html')


def m500(request):
    return render(request, 'blog/500.html')
