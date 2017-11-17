# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect

from texas.forms import SignupForm, LoginForm
from texas.models import *


# Create your views here.
def home(request):
    context = {}
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('lobby'))
    return render(request, 'homepage.html', context)


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    signupform = SignupForm(request.POST)
    if not signupform.is_valid():
        return render(request, 'signup.html')

    new_user = User.objects.create_user(
        username=signupform.cleaned_data['username'],
        password=signupform.cleaned_data['password'],
        first_name=signupform.cleaned_data['first_name'],
        last_name=signupform.cleaned_data['last_name'],
        email=signupform.cleaned_data['email'])
    new_user.save()

    user = authenticate(
        request,
        username=signupform.cleaned_data['username'],
        password=signupform.cleaned_data['password'])
    if user is not None:
        login(request, user)
        return redirect(reverse('lobby'))
    else:
        return render(request, 'signup.html')


def log_in(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'homepage.html')

    login_form = LoginForm(request.POST)
    if not login_form.is_valid():
        context['errors'] = login_form.errors.as_data()['__all__'][0]
        #print(login_form.errors.as_data())
        return render(request, 'homepage.html', context)

    user = authenticate(
        request,
        username=login_form.cleaned_data['username'],
        password=login_form.cleaned_data['password'])
    if user is not None:
        login(request, user)
        return redirect(reverse('lobby'))
    else:
        context['errors'] = ['Username and password do not match.']
        return render(request, 'homepage.html', context)


@login_required
def lobby(request):
    context = {}
    return render(request, 'lobby.html', context)


@login_required
def profile(request):
    context = {}
    return render(request, 'profile.html', context)


@transaction.atomic
def tutorial(request):
    context = {}
    print(request.user)
    if request.user.is_authenticated():
        context['logged_in'] = 1
        print('user logged in')
    else:
        print('user not logged in')
    return render(request, 'tutorial.html', context)


@login_required
def playroom(request, deskname):
    context = {}
    desk = get_object_or_404(Desk_info, desk_name=deskname)
    if desk.is_start == False:
        return render(request, 'playroom.html', context)

    user = User_Game_play.objects.filter(desk=desk)
    if user:
        return render(request, 'playroom.html', context)
    else:
        context[
            'errors'] = 'Permission denied: there is an ongoing game in this room, please try another.'
        return render(request, 'lobby.html', context)


@login_required
@transaction.atomic
def log_out(request):
    logout(request)
    context = {}
    return render(request, 'homepage.html', context)
