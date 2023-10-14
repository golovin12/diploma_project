import random
import warnings

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from .forms import StudentForm, DemodulateInfluenceSNRFrom
from .models import Student, StudentLab1
from .utils import convert_base, for_test, get_lab2_tasks_by_student, get_lab3_tasks_by_student, \
    get_lab4_by_student

warnings.filterwarnings('ignore')


@require_http_methods(["GET", "POST"])
def student_login(request: WSGIRequest):
    next_page = request.GET.get('next')
    form = StudentForm
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            student = form.get_user()
            login(request, student)
            return HttpResponseRedirect(next_page or reverse('detect:lab1_example'))
    return render(request, 'detect/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def student_logout(request: WSGIRequest):
    logout(request)
    return HttpResponseRedirect(reverse('detect:home'))


@require_GET
def home_page(request: WSGIRequest):
    """Главная страница"""
    with open('theory/glavn.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    data = {"header": "Лабораторная работа на тему 'Детектирование сигналов в современных системах связи'",
            "text": text}
    return render(request, 'detect/home.html', context=data)


@require_GET
def theory1(request: WSGIRequest):
    with open('theory/theory1.txt', 'r', encoding='UTF-8') as f:
        text = f.readlines()
    data = {"header": "1. Общие сведения о задаче детектирования",
            "text": text}
    return render(request, 'detect/theory1.html', context=data)


@require_GET
def theory2(request: WSGIRequest):
    with open('theory/theory2.txt', 'r', encoding='UTF-8') as file:
        text = file.readlines()
    data = {"header": "2. Классификация методов детектирования",
            "text": text
            }
    return render(request, 'detect/theory2.html', context=data)


@require_GET
def theory3(request: WSGIRequest):
    with open('theory/theory3.txt', 'r', encoding='UTF-8') as file:
        text = file.readlines()
    data = {"header": "3. Перспективы развития методов детектирования",
            "text": text
            }
    return render(request, 'detect/theory3.html', context=data)


@require_GET
@never_cache
def result_is_db(request: WSGIRequest):
    """Возвращает информацию о статусе выполнения заданий студентами"""
    # todo отображать прогресс по лабам и тесту в виде таблицы.
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


@login_required(login_url="/detect/student_login/")
@require_http_methods(["GET", "POST"])
@never_cache
def final_test(request: WSGIRequest):
    # todo привязать набор вопросов к пользователю
    global otveti_for_users
    c = 0
    form = StudentForm()  # Создаются поля для ввода Имени, Фамилии и Группы
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
            return render(request, 'detect/final_test.html',
                          context={"zagolovok": zagolovok, "voprosi": voprosi, "form": form, "result": result,
                                   "id": pk})
    else:  # Когда пользователь только заходит на страницу теста, то для него формируются вопросы и ответы, которые запоминаются в функции func5
        zagolovok, voprosi, otveti = for_test('tests/test1.txt',
                                              15)  # Получение из файла перемешанных вопросов и ответов к ним.
        pk = znach(voprosi, otveti)
        otveti_for_users.append(pk)
        result = "Введите свои данные и проходите тест:"
        return render(request, 'detect/final_test.html',
                      context={"zagolovok": zagolovok, "voprosi": voprosi, "form": form, "result": result,
                               "id": pk})


@login_required(login_url="/detect/student_login/")
@require_GET
def lab1_example(request: WSGIRequest):
    return render(request, 'detect/lab1_example.html', {'form': DemodulateInfluenceSNRFrom})


@login_required(login_url="/detect/student_login/")
@require_http_methods(["POST", "GET"])
@never_cache
def laboratory1(request: WSGIRequest):
    form = DemodulateInfluenceSNRFrom
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            data = form.get_context_data()
            if data['is_complete']:
                StudentLab1.objects.get_or_create(student=request.user, modulation=data['modulation'], is_complete=True)
            data['form'] = form
            return render(request, 'detect/laboratory1.html', context=data)
    return render(request, 'detect/lab1_example.html', context={"form": form, 'hide_example': True})


@login_required(login_url="/detect/student_login/")
@require_http_methods(["POST", "GET"])
@never_cache
def laboratory2(request: WSGIRequest):
    lab2_tasks = get_lab2_tasks_by_student(request.user)
    if request.method == "POST":
        for lab2 in lab2_tasks:
            if not lab2.is_complete and request.POST.get(lab2.modulation) == lab2.signal:
                lab2.is_complete = True
                lab2.save()
    return render(request, 'detect/laboratory2.html', context={'lab2_tasks': lab2_tasks})


@login_required(login_url="/detect/student_login/")
@require_http_methods(["POST", "GET"])
@never_cache
def laboratory3(request: WSGIRequest):
    lab3_tasks = get_lab3_tasks_by_student(request.user)
    if request.method == "POST":
        for lab3 in lab3_tasks:
            if not lab3.is_complete and request.POST.get(f'signal-{lab3.multiplier}') == lab3.signal:
                lab3.is_complete = True
                lab3.save()
    return render(request, 'detect/laboratory3.html', context={"lab3_tasks": lab3_tasks})


@login_required(login_url="/detect/student_login/")
@require_http_methods(["POST", "GET"])
@never_cache
def laboratory4(request: WSGIRequest):
    lab4 = get_lab4_by_student(request.user)
    if request.method == "POST":
        if not lab4.is_complete and request.POST.get('signal') == lab4.signal:
            lab4.is_complete = True
            lab4.save()
    return render(request, 'detect/laboratory4.html', context={"lab4": lab4})


# Запоминает вопросы пользователя
otveti_for_users = []
otveti_slovar = {}


def znach(voprosi, otveti):
    # Функция принимает блок вопросов и ответов, сохраняет их под определённым id и отправляет этот id пользователю
    global otveti_slovar
    t = random.randint(-99999999, 99999999)
    while otveti_slovar.get(str(t)) != None:
        t = random.randint(-99999999, 99999999)
    otveti_slovar[str(t)] = [voprosi, otveti]
    return str(t)
