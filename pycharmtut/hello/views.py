from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


# Create your views here.

def hello_view(*args, **kwargs):
    return JsonResponse({'foo':'bar'})
