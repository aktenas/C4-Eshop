from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render (request, 'home/index.html', {})
def tasks(request):
    return render (request, 'home/tasks.html', {})
def contact(request):
    return render (request, 'home/contact.html', {})
def about(request):
    return render (request, 'home/about.html', {})
def reviews(request):
    return render (request, 'home/reviews.html', {})