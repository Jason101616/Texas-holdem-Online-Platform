# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import datetime

# Create your models here.
class Game_info(models.Model):
    game_name = models.CharField(max_length=50)
    current_version = models.CharField(max_length=50)
    process_name = models.CharField(max_length=50)
    is_maintain = models.BooleanField()
    max_num_players = models.IntegerField(default=8)
    min_num_players = models.IntegerField(default=2)

    def __str__(self):
        return self.game_name

class User_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=420, blank=True)
    age = models.IntegerField(blank=True, default=0)
    profile_picture = models.FileField(
        upload_to='profile_pictures/', default="profile_pictures/kennyS.jpg")
    followings = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')
    email_confirmed = models.BooleanField(default=False)
    gender = models.CharField(max_length=20)
    desk = models.ForeignKey(Desk_info, on_delete=models.CASCADE)   # a desk can have many users

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        User_info.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Desk_info(models.Model):
    start_time = models.DateTimeField(default=datetime.datetime.now())
    end_time = models.DateTimeField(default=datetime.datetime.now())
    num_players = models.IntegerField()
    current_status = models.CharField()

class Card_info(models.Model):
    color = models.CharField()
    number = models.CharField()
    in_deck = models.BooleanField()
    desk = models.ForeignKey(Desk_info, on_delete=models.CASCADE)

class Game_play(models.Model):
    start_time = models.DateTimeField(default=datetime.datetime.now())
    end_time = models.DateTimeField(default=datetime.datetime.now())
    user = models.OneToOneField(User_info, on_delete=models.CASCADE)
    action = models.CharField()
    current_status = models.CharField() # user's status
