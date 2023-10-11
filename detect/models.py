from django.db import models
from django.utils import timezone


class Question(models.Model):
    name = models.CharField(max_length=255, verbose_name='Вопрос')
    image = models.ImageField(verbose_name='Картинка к вопросу', max_length=200, blank=True,
                              upload_to='models.Question.image/')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(verbose_name="Текст ответа", max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'


class Student(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя')
    surname = models.CharField(max_length=20, verbose_name='Фамилия')
    group = models.CharField(max_length=20, verbose_name='Группа')

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f'{self.group}: {self.surname} {self.name}'


class StudentTest(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, related_name='questions')
    test_percent = models.DecimalField(verbose_name='Процент выполнения теста', max_digits=5, decimal_places=2,
                                       default=0)
    attempt = models.PositiveIntegerField(default=0, blank=True)
    end_dt = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        ordering = ('-end_dt',)

    def __str__(self):
        return f'{self.student}: {self.test_percent}'


class PageData(models.Model):
    slug = models.SlugField(verbose_name='Название страницы', unique=True)
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    text = models.TextField(verbose_name='Текст')
