# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect

from django.core.mail import send_mail, EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token

from texas.forms import *
from texas.models import *

big_blind_min = 200


# Create your views here.
def home(request):
    context = {}
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('lobby'))
    return render(request, 'homepage.html', context)


def signup(request):
    context = {}
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
    new_user.is_active = False
    new_user.save()

    message = render_to_string(
        'active_email.html', {
            'user': new_user,
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
            'token': account_activation_token.make_token(new_user),
        })
    mail_subject = 'Activate your account.'
    to_email = new_user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    context[
        'message'] = 'Please confirm your email address to complete the registration.'
    context['title'] = 'Please Confirm Email'
    return render(request, 'message.html', context)


def activate(request, uidb64, token):
    context = {}
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        context['message'] = "Your account is now activated."
        return render(request, 'message.html', context)
    else:
        context['message'] = 'Activation link is invalid.'
        return render(request, 'message.html', context)


def forgetpassword(request):
    context = {}
    errors = []
    context['errors'] = errors
    if request.method == 'GET':
        context['form'] = Reset_password()
        return render(request, 'reset.html', context)

    form = Reset_password(request.POST)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'reset.html', context)

    user = get_object_or_404(User, username=request.POST['username'])
    if user.email != request.POST['email']:
        context['message'] = "Your email and username does not match"
        return render(request, 'message.html', context)

    message = render_to_string(
        'forget_pass.html', {
            'user': user,
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
    mail_subject = 'Reset your password.'
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    context[
        'message'] = 'Please confirm your email address to reset your password.'
    return render(request, 'message.html', context)


def morechips(request):
    context = {}
    errors = []
    context['errors'] = errors
    if request.method == 'GET':
        context['form'] = ChipEmail()
        return render(request, 'morechips.html', context)

    form = ChipEmail(request.POST)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'morechips.html', context)

    if request.user.email == request.POST['email']:
        context['form'] = form
        context['errors'] = "You cannot send emails to yourself."
        return render(request, 'morechips.html', context)

    user = request.user

    message = render_to_string(
        'get_chips.html', {
            'user': user,
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
    mail_subject = 'Help your friend get additional chips.'
    to_email = request.POST['email']
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    context['message'] = 'Please ask your friend to confirm the email.'
    context['title'] = "Confirm email."
    return render(request, 'message.html', context)


def reset(request, uidb64, token):
    context = {}
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        context['user'] = user
        context['form'] = Register_password()
        return render(request, 'reset_pass.html', context)
    else:
        context['message'] = 'Activation link is invalid.'
        context['title'] = 'Invalid Link'
        return render(request, 'message.html', context)


def resetpass(request):
    context = {}
    user = request.POST['user']
    user = get_object_or_404(User, username=user)
    user.set_password(request.POST['password1'])
    user.save()
    login(request, user)
    return HttpResponseRedirect(reverse('lobby'))


def chips(request, uidb64, token):
    context = {}
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user_info = User_info.objects.get(user=user)
        user_info.chips = user_info.chips + 10000
        user_info.save()
        context[
            'message'] = "You have successfully gained 10000 coins for your friend! Thank you for your help!"
        context['title'] = "Success"
        return render(request, 'message.html', context)
    else:
        context['message'] = 'Link is invalid.'
        context['title'] = 'Invalid Link'
        return render(request, 'message.html', context)


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
    if 'errors' in request.session:
        context['errors'] = request.session['errors']
        del request.session['errors']
    desk_form = DeskForm()
    context['desk_form'] = desk_form
    desks = Desk_info.objects.all()
    context['desks'] = desks

    return render(request, 'lobby.html', context)


@login_required
def profile(request):
    context = {}
    context['user'] = request.user
    context['profile'] = User_info.objects.get(user=request.user)
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
    context['deskname'] = deskname
    if request.method != 'GET':
        print("invalid request!")
        return
    if desk.is_start:
        context['errors'] = [
            'Permission denied: there is an ongoing game in this room, please try another.'
        ]
    elif user_info.chips < big_blind_min:
        print('cannot get into the room')
        request.session['errors'] = 'You don\'t have enough chips'
    else:
        return render(request, 'playroom.html', context)
    return redirect(reverse('lobby'))


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
        player_info = {
            'username': username,
            'position': pos,
            'chips': player.user.chips
        }
        context_players.append(player_info)

    context['players'] = context_players

    return render(
        request,
        'json/newplayers.json',
        context,
        content_type='application/json')


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

    return render(
        request, 'json/getjob.json', context, content_type='application/json')


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

    return render(
        request,
        'json/position.json',
        context,
        content_type='application/json')


@login_required
@transaction.atomic
def newplay(request):
    print("enter newplay")
    if request.method == 'POST':
        print("post in newplay")
        user_info = get_object_or_404(User_info, user=request.user)
        if user_info.chips < big_blind_min:
            request.session['errors'] = 'You don\'t have enough chips'
            return redirect(reverse('lobby'))
        desk_form = DeskForm(request.POST)
        if not desk_form.is_valid():
            return redirect(reverse('lobby'))

        user_info = User_info.objects.get(user=request.user)
        if user_info.chips < big_blind_min:
            return redirect(reverse('lobby'))

        room_id = str(desk_form.cleaned_data['desk_name'])
        this_user_info = User_info.objects.get(user=request.user)
        new_desk = Desk_info(
            desk_name=str(desk_form.cleaned_data['desk_name']),
            owner=this_user_info)
        new_desk.save()
        return redirect(reverse('playroom', kwargs={'deskname': room_id}))
    print("return lobby")
    return redirect(reverse('lobby'))


def update_button(request):
    desks = Desk_info.objects.all()
    context = {'desks': desks}
    return render(
        request, 'json/desks.json', context, content_type='application/json')
