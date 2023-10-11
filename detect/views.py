import random
import warnings

import matplotlib.pyplot as plt
from commpy.channels import awgn
from django.views.decorators.http import require_GET, require_http_methods
from scipy.fft import fft, ifft

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from modulation_script import QAMModem, PSKModem
from .forms import UserForm
from .models import Student
from .utils import convert_base, for_test, graf, for_percent, for_lab1, for_lab2, sozvezd

warnings.filterwarnings('ignore')

# Запоминает вопросы пользователя
otveti_for_users = []
otveti_slovar = {}
file_lab1 = []
file_lab2 = []
file_lab4 = []
file_sozvezd2 = []


def znach(voprosi, otveti):
    # Функция принимает блок вопросов и ответов, сохраняет их под определённым id и отправляет этот id пользователю
    global otveti_slovar
    t = random.randint(-99999999, 99999999)
    while otveti_slovar.get(str(t)) != None:
        t = random.randint(-99999999, 99999999)
    otveti_slovar[str(t)] = [voprosi, otveti]
    return str(t)


@require_GET
def home_page(request: WSGIRequest):
    """Главная страница"""
    with open('theory/glavn.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    data = {"header": "Лабораторная работа на тему 'Детектирование сигналов в современных системах связи'",
            "text": text}
    return render(request, 'detect/home.html', context=data)


@require_GET
def theory1(request):
    with open('theory/theory1.txt', 'r', encoding='UTF-8') as f:
        text = f.readlines()
    data = {"header": "1. Общие сведения о задаче детектирования",
            "text": text}
    return render(request, 'detect/theory1.html', context=data)


@require_GET
def theory2(request):
    with open('theory/theory2.txt', 'r', encoding='UTF-8') as f:
        text = f.readlines()
    data = {"header": "2. Классификация методов детектирования",
            "text": text
            }
    return render(request, 'detect/theory2.html', context=data)


@require_GET
def theory3(request):
    with open('theory/theory3.txt', 'r', encoding='UTF-8') as f:
        text = f.readlines()
    data = {"header": "3. Перспективы развития методов детектирования",
            "text": text
            }
    return render(request, 'detect/theory3.html', context=data)


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
        return render(request, 'detect/laborathory1.html',
                      context={"modulat": modulat, "t_modulat": t_modulat, "msg": msg, "c": c,
                               "demodulated": d, "itog": itog, "f1": f1, "f2": f2, "snr": snr})
    else:
        return render(request, 'detect/vhod.html')


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
        return render(request, 'detect/result.html', context={"result": result})
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
        return render(request, 'detect/laborathory2.html', context={"d": det, "vih_put": vih_put, "put_sozv": put_sozv})


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
        return render(request, 'detect/result.html', context={"result": result})
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
        return render(request, 'detect/laborathory3.html', context={"spisok": spisok, "mess": mess})


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
        return render(request, 'detect/result.html', context={"result": result})
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
        return render(request, 'detect/laborathory4.html', context={"put": put, "signal": signal, "vihod": vihod})


@require_GET
@never_cache
def result_is_db(request: WSGIRequest):
    """Возвращает информацию о статусе выполнения заданий студентами"""
    page_number = request.GET.get('page')
    students = Student.objects.all()
    paginator = Paginator(students, 50)
    students_results = []
    for index, student in enumerate(paginator.get_page(page_number), start=1):
        student: Student
        result = f"{index}) {student}"
        result += f" прошёл тест на {student.test_percent}% "
        result += f"(дата прохождения: {student.create_dt.strftime('%d.%m.%Y')})"
        students_results.append(result)
    return render(request, 'detect/result_is_db.html', context={"spisok": students_results})


@require_http_methods(["GET", "POST"])
@never_cache
def tests(request):
    # Выводит Тестовые вопросы, просит пользователя авторизоваться и, при успешном выполнении теста, выводит результат.
    global otveti_for_users
    c = 0
    userform = UserForm()  # Создаются поля для ввода Имени, Фамилии и Группы
    if request.method == "POST":  # Проверяется, вводил ли пользователь свои данные и ответил ли на вопросы
        # Т.к. изначально при входе на страницу ничего не введено, то эта функция вызывается после else (поэтому сначала надо смотреть на работу этого пункта)
        name = request.POST.get("name")
        surname = request.POST.get("family")
        group = request.POST.get("group")
        pk = request.POST.get("id")
        voprosi, otveti = otveti_slovar.get(pk)[0], otveti_slovar.get(pk)[1]
        for i in range(len(voprosi)):  # Перебирает каждый ответ, выбранный пользователем
            a = request.POST.get(
                str(voprosi[i][5]))  # Извлекаю из каждого вопроса варианты ответов, выбранные пользователем
            if a == otveti[i]:  # Сверяю извлеченный ответ с правильным ответом
                c += 1
        test_percent = 100 * c // len(voprosi)  # Подсчёт процента правильных ответов пользователя

        if test_percent >= 80:  # Если процент больше 80, то создаю в БД строку, в которой записываются Данные пользователя и процент правильных ответов,
            # а также отправляет пользователя на страницу, где будет написан результат выполнения теста
            Student.objects.create(name=name, surname=surname, group=group, test_percent=test_percent)
            otveti_for_users.remove(pk)
            otveti_slovar.pop(pk)
            result = "{0} {1} из группы {2}. Вы прошли тест на: {3}%. Покажите результат преподавателю!".format(name,
                                                                                                                surname,
                                                                                                                group,
                                                                                                                test_percent)
            return render(request, 'detect/result.html', context={"result": result})
        else:  # Если процент выполнения меньше 80, то заново формируются блоки вопросов и ответов, пользователь отправляется заново проходить тест
            zagolovok, voprosi, otveti = for_test('tests/test1.txt', 15)
            otveti_for_users.remove(pk)
            otveti_slovar.pop(pk)
            pk = znach(voprosi, otveti)
            otveti_for_users.append(pk)
            result = "Вы прошли тест на: {}%. Попробуйте ещё раз!".format(test_percent)
            return render(request, 'detect/tests.html',
                          context={"zagolovok": zagolovok, "voprosi": voprosi, "form": userform, "result": result,
                                   "id": pk})
    else:  # Когда пользователь только заходит на страницу теста, то для него формируются вопросы и ответы, которые запоминаются в функции func5
        zagolovok, voprosi, otveti = for_test('tests/test1.txt',
                                              15)  # Получение из файла перемешанных вопросов и ответов к ним.
        pk = znach(voprosi, otveti)
        otveti_for_users.append(pk)
        result = "Введите свои данные и проходите тест:"
        return render(request, 'detect/tests.html',
                      context={"zagolovok": zagolovok, "voprosi": voprosi, "form": userform, "result": result,
                               "id": pk})
