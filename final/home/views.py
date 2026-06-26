from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def home(request):
    return render (request, 'home/welcome.html', {})
def tasks(request):
    return render (request, 'home/tasks.html', {})
def contact(request):
    return render (request, 'home/contact.html', {})
