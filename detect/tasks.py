# todo Хранить записи 4 месяца после создания, старые - удалять
if Student.objects.count() > 100:
    while Student.objects.count() > 50:
        g = Person.objects.values_list("id").first()[0]
        Person.objects.filter(id=g).delete()

# todo через 2 дня удалять все media
