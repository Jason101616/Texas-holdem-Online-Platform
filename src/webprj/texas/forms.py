#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from texas.models import *

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email']

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        username = self.cleaned_data.get('username')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        password = self.cleaned_data.get('password')
        email = self.cleaned_data.get('email')
        if not username:
            raise forms.ValidationError('Username is required.')
        if not first_name:
            raise forms.ValidationError('First name is required.')
        if not last_name:
            raise forms.ValidationError('Last name is required.')
        if not password:
            raise forms.ValidationError('Password is required.')
        if not email:
            raise forms.ValidationError('Email is required.')
        return cleaned_data

class ChipEmail(forms.Form):
    email = forms.EmailField()
    def clean(self):
        cleaned_data = super(ChipEmail, self).clean()
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email is required.')
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label="Username")
    password = forms.CharField(max_length=32, label="Password", widget = forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not username and not password:
            raise forms.ValidationError('Username and password are required.')
        if not username:
            raise forms.ValidationError('Username is required.')
        if not password:
            raise forms.ValidationError('Password is required.')
        return cleaned_data


class DeskForm(forms.ModelForm):
    desk_name = forms.CharField(max_length=42, widget = forms.TextInput(attrs = {'placeholder' : 'desk name'}))

    class Meta:
        model = Desk_info
        fields = ['desk_name']

    def clean(self):
        cleaned_data = super(DeskForm, self).clean()
        desk_name = self.cleaned_data.get('desk_name')
        if not desk_name:
            raise forms.ValidationError("Desk Name are required.")
        for s in desk_name:
            if not s.isalnum():
                raise forms.ValidationError("Desk Name can only be number of characters.")
        return cleaned_data

class Reset_password(forms.Form):
    username = forms.CharField(max_length = 420, widget = forms.TextInput(attrs = {'placeholder' : 'Username'}))
    email = forms.EmailField(widget = forms.TextInput(attrs = {'placeholder' : 'Email'}))

    def clean(self):
        cleaned_data = super(Reset_password, self).clean()
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if not username and not email:
            raise forms.ValidationError('Username and Email are required.')
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Username is required.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email is required.')
        return email

class Register_password(forms.Form):
    password1 = forms.CharField(max_length=50, widget = forms.PasswordInput(attrs = {'placeholder' : 'Set a password'}), label = "* Password")
    password2 = forms.CharField(max_length=50, widget = forms.PasswordInput(attrs = {'placeholder' : 'Confirm password'}), label = "* Confirm Password")

    def clean(self):
        cleaned_data = super(Register_password, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        return cleaned_data

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1:
            raise forms.ValidationError('Password is required.')
        elif password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match!')
        if not password1 and not password2:
            raise forms.ValidationError('Passwords are required.')
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise forms.ValidationError('Confirm password is required.')
        return password2 
