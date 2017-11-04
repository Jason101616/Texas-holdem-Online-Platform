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

def lobby(request):
    context = {}
    return render(request, 'lobby.html', context)

def profile(request):
    context = {}
    return render(request, 'profile.html', context)

def tutorial(request):
    context = {}
    return render(request, 'tutorial.html', context)

def playroom(request):
    context = {}
    return render(request, 'playroom.html', context)
