from django.db import models
from django.utils import timezone



class Person(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя')
    family = models.CharField(max_length=20,verbose_name='Фамилия')
    group = models.CharField(max_length=20,verbose_name='Группа')
    percent = models.IntegerField(verbose_name='Процент выполнения')
    created_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    def __str__(self):
        return self.name, self.family