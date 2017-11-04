# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


# Create your views here.
def home(request):
    context = {}
    return render(request, 'homepage.html', context)

def signup(request):
    context = {}
    return render(request, 'signup.html', context)

def dashboard(request):
    context = {}
    return render(request, 'dashboard.html', context)
