from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
# Create your views here.

def home_test(request):
    return HttpResponse("Welcome to the Common Threads Home Page!", status=200)