from django.shortcuts import render


def m304(request):
    return render(request, 'diploma/304.html')


def m400(request, exception):
    return render(request, 'diploma/400.html')


def m403(request, exception):
    return render(request, 'diploma/403.html')


def m404(request, exception):
    return render(request, 'diploma/404.html')


def m405(request):
    return render(request, 'diploma/405.html')


def m410(request):
    return render(request, 'diploma/410.html')


def m500(request):
    return render(request, 'diploma/500.html')
