# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import datetime


# Create your models here.
class User_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=420, blank=True)
    age = models.IntegerField(blank=True, default=0)
    profile_picture = models.FileField(
        upload_to='profile_pictures/', default="profile_pictures/king.jpeg")
    followings = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')
    email_confirmed = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        User_info.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.user_info.save()


class Desk_info(models.Model):
    desk_name = models.CharField(max_length=40, default="test")
    owner = models.OneToOneField(
        User_info, on_delete=models.CASCADE, null=True)
    capacity = models.IntegerField(default=9)
    current_capacity = models.IntegerField(default=9)
    is_start = models.BooleanField(default=False)
    position_queue = models.CharField(max_length=40, default="012345678")
    player_queue = models.CharField(max_length=20, default="")
    player_queue_pointer = models.IntegerField(default=0)
    five_cards_of_desk = models.CharField(max_length=50, default='')

    def __str__(self):
        return "desk_name: %s, owner: %s, capacity: %d, current: %d, is_start: %d, position_queue: %s"%\
               (self.desk_name, self.owner, self.capacity, self.current_capacity, self.is_start, self.position_queue)


class User_Game_play(models.Model):
    user = models.OneToOneField(User_info, on_delete=models.CASCADE)
    position = models.IntegerField(default=10)
    is_fold = models.BooleanField(default=False)
    desk = models.ForeignKey(
        Desk_info, on_delete=models.CASCADE,
        null=True)  # a desk can have many users
    user_cards = models.CharField(max_length=30, default='')

    def __str__(self):
        return "desk_name: %s, username: %s, position: %d"%\
               (self.desk.desk_name, self.user.user.username, self.position)


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
