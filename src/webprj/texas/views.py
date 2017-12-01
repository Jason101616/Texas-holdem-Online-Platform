# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect

from texas.forms import *
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
    desk_form = DeskForm()
    context['desk_form'] = desk_form
    desks = Desk_info.objects.all()
    context['desks'] = desks
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
    return render(request, 'tutorial.html', context)


@login_required
def playroom(request, deskname):
    context = {}
    desk = get_object_or_404(Desk_info, desk_name=deskname)
    user_info = get_object_or_404(User_info, user=request.user)
    user_game = User_Game_play.objects.filter(desk=desk, user=user_info)

    context['user'] = request.user
    context['user_chips'] = user_info.chips

    if not desk.is_start:
        return render(request, 'playroom.html', context)

    if user_game:
        return render(request, 'playroom.html', context)
    else:
        context['errors'] = [
            'Permission denied: there is an ongoing game in this room, please try another.'
        ]
        return render(request, 'lobby.html', context)


@login_required
@transaction.atomic
def log_out(request):
    logout(request)
    context = {}
    return render(request, 'homepage.html', context)


@login_required
@transaction.atomic
def addplayer(request):
    context = {}
    context_players = []

    loguser_mod = get_object_or_404(User_info, user=request.user)
    loguser = get_object_or_404(User_Game_play, user=loguser_mod)

    players = User_Game_play.objects.filter(desk=loguser.desk)

    for player in players:
        username = player.user.user.username
        pos = player.position - loguser.position
        if pos < 0:
            pos = pos + 9
        player_info = {'username': username, 'position': pos, 'chips': player.user.chips}
        context_players.append(player_info)

    context['players'] = context_players

    return render(request, 'json/newplayers.json', context, content_type='application/json')


@login_required
@transaction.atomic
def getjob(request, pos_big, pos_small, pos_dealer):
    loguser_mod = get_object_or_404(User_info, user=request.user)
    loguser = get_object_or_404(User_Game_play, user=loguser_mod)
    context = {}

    pos1 = int(pos_big) - loguser.position
    if pos1 < 0:
        pos1 = pos1 + 9

    pos2 = int(pos_small) - loguser.position
    if pos2 < 0:
        pos2 = pos2 + 9

    pos3 = int(pos_dealer) - loguser.position
    if pos3 < 0:
        pos3 = pos3 + 9

    context = {'big_blind': pos1, 'small_blind': pos2, 'dealer': pos3}

    return render(request, 'json/getjob.json', context, content_type='application/json')


@login_required
@transaction.atomic
def get_position(request):
    loguser_mod = get_object_or_404(User_info, user=request.user)
    loguser = get_object_or_404(User_Game_play, user=loguser_mod)
    context = {}

    '''pos = int(position) - 1 - loguser.position
    if pos < 0:
        pos = pos + 9'''

    context = {'position': loguser.position}

    return render(request, 'json/position.json', context, content_type='application/json')


@login_required
@transaction.atomic
def newplay(request):
    print("enter newplay")
    if request.method == 'POST':
        print ("post")
        desk_form = DeskForm(request.POST)
        if not desk_form.is_valid():
            return redirect(reverse('lobby'))
        room_id = str(desk_form.cleaned_data['desk_name'])
        this_user_info = User_info.objects.get(user=request.user)
        new_desk = Desk_info(desk_name=str(desk_form.cleaned_data['desk_name']), owner=this_user_info)
        new_desk.save()
        return redirect(reverse('playroom', kwargs={'deskname': room_id}))
    print("return lobby")
    return redirect(reverse('lobby'))
