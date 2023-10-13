import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .consts import modulation_choices

signal_validator = RegexValidator(r'^[0,1]*$')


class Student(AbstractBaseUser):
    username = models.UUIDField('username', unique=True, default=uuid.uuid4)
    password = models.CharField('password', max_length=128, blank=True, default='')
    name = models.CharField(max_length=200, verbose_name='Имя')
    surname = models.CharField(max_length=200, verbose_name='Фамилия')
    group = models.CharField(max_length=20, verbose_name='Группа')

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f'{self.group}: {self.surname} {self.name}'


class Question(models.Model):
    name = models.CharField(max_length=255, verbose_name='Вопрос')
    image = models.ImageField(verbose_name='Картинка к вопросу', max_length=200, blank=True,
                              upload_to='models.Question.image/')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.CharField(verbose_name="Текст ответа", max_length=255)
    is_correct = models.BooleanField(default=False, verbose_name='Корректный',
                                     help_text='Выберите, должен ли быть данный вариант ответа правильным')

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'


class StudentTest(models.Model):
    student = models.OneToOneField(Student, verbose_name='Студент', on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, related_name='questions')
    test_percent = models.DecimalField(verbose_name='Процент выполнения теста', max_digits=5, decimal_places=2,
                                       default=0)
    attempts = models.PositiveIntegerField(verbose_name='Количество попыток', default=0, blank=True)
    end_dt = models.DateTimeField(verbose_name='Время окончания', default=timezone.now, blank=True)

    class Meta:
        ordering = ('-end_dt',)

    def __str__(self):
        return f'{self.student}: {self.test_percent}'


class StudentLab1(models.Model):
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.CASCADE)
    modulation = models.CharField(verbose_name='Тип модуляции', max_length=7, choices=modulation_choices)
    is_complete = models.BooleanField(default=False, verbose_name='Выполнено',
                                      help_text='Становится True если задание выполнено')


class StudentLab2(models.Model):
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.CASCADE)
    modulation = models.CharField(verbose_name='Тип модуляции', max_length=7, choices=modulation_choices)
    signal = models.CharField(verbose_name='Сигнал', max_length=8, validators=[signal_validator])
    signal_image = models.ImageField(verbose_name='Изображение сигнала', max_length=200, blank=True,
                                     upload_to='models.StudentLab2.signal_image/%Y/')
    stars_image = models.ImageField(verbose_name='Сигнальное созвездие', max_length=200, blank=True,
                                    upload_to='models.StudentLab2.stars_image/%Y/')
    is_complete = models.BooleanField(default=False, verbose_name='Детектирован',
                                      help_text='Становится True если сигнал детектирован')


class StudentLab3(models.Model):
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.CASCADE)
    signal = models.CharField(verbose_name='Сигнал', max_length=80, validators=[signal_validator])
    signal_complex = models.CharField(verbose_name='Сигнал в виде комплексных чисел', max_length=3000)
    is_complete = models.BooleanField(default=False, verbose_name='Детектирован',
                                      help_text='Становится True если сигнал детектирован')


class StudentLab4(models.Model):
    student = models.OneToOneField(Student, verbose_name='Студент', on_delete=models.CASCADE)
    signal = models.CharField(verbose_name='Сигнал', max_length=96, validators=[signal_validator])
    signal_complex = models.CharField(verbose_name='Сигнал в виде комплексных чисел', max_length=4000)
    signal_image = models.ImageField(verbose_name='Изображение сигнала', max_length=200, blank=True,
                                     upload_to='models.StudentLab4.signal_image/%Y/')
    is_complete = models.BooleanField(default=False, verbose_name='Детектирован',
                                      help_text='Становится True если сигнал детектирован')


class PageData(models.Model):
    slug = models.SlugField(verbose_name='Название страницы', unique=True)
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    text = models.TextField(verbose_name='Текст')
