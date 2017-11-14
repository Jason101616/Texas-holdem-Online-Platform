# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import datetime

# Create your models here.

class Desk_info(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    num_players = models.IntegerField()
    current_status = models.CharField(max_length=50)

class User_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    bio = models.TextField(max_length=420, blank=True)
    age = models.IntegerField(blank=True, default=0)
    profile_picture = models.FileField(
        upload_to='profile_pictures/', default="profile_pictures/XXX.jpg")
    followings = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')
    email_confirmed = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, blank=True)
    desk = models.ForeignKey(
        Desk_info, on_delete=models.CASCADE,
        null=True)  # a desk can have many users

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        User_info.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.user_info.save()


class Game_info(models.Model):
    game_name = models.CharField(max_length=50)
    current_version = models.CharField(max_length=50)
    process_name = models.CharField(max_length=50)
    is_maintain = models.BooleanField()
    max_num_players = models.IntegerField(default=8)
    min_num_players = models.IntegerField(default=2)

    def __str__(self):
        return self.game_name


class Card_info(models.Model):
    color = models.CharField(max_length=20)
    number = models.CharField(max_length=20)
    in_deck = models.BooleanField()
    desk = models.ForeignKey(Desk_info, on_delete=models.CASCADE)


class Game_play(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    user = models.OneToOneField(User_info, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)
    current_status = models.CharField(max_length=50)  # user's status
