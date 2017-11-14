#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from texas.models import User_info

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email']