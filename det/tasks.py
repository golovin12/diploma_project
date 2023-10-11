# Удаление лишних записей из базы данных (через месяц)
if Student.objects.count() > 100:
    while Student.objects.count() > 50:
        g = Person.objects.values_list("id").first()[0]
        Person.objects.filter(id=g).delete()
