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
    chips = models.IntegerField(default=10000)
    game_played = models.IntegerField(default = 0)
    game_win = models.IntegerField(default = 0)
    game_lose = models.IntegerField(default = 0)

    def __str__(self):
        return "username: %s, chips: %d" % (self.user.username, self.chips)


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        User_info.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.user_info.save()


class Desk_info(models.Model):
    desk_name = models.CharField(
        max_length=40, default="test", blank=False, primary_key=True)
    owner = models.OneToOneField(
        User_info, on_delete=models.CASCADE, null=True)
    capacity = models.IntegerField(default=9)
    current_capacity = models.IntegerField(default=9)
    is_start = models.BooleanField(default=False)
    position_queue = models.CharField(max_length=40, default="012345678")

    player_queue = models.CharField(max_length=20, default="")
    player_queue_pointer = models.IntegerField(default=0)
    five_cards_of_desk = models.CharField(max_length=50, default='')

    current_largest_chips_this_game = models.IntegerField(default=0)
    current_round_largest_chips = models.IntegerField(default=0)
    # current desk, it will give to the winner in the end of the current game.
    pool = models.IntegerField(default=0)
    # pre-flop, flop, turn, river
    phase = models.CharField(max_length=10, default='pre_flop')

    next_dealer = models.IntegerField(default=-1)

    def __str__(self):
        return "desk_name: %s, owner: %s, capacity: %d, current: %d, is_start: %d, position_queue: %s, player_queue: %s, player_queue_pointer: %d, five_cards_of_desk: %s, current_largest_chips_this_game: %d, pool: %d" % (
            self.desk_name, self.owner, self.capacity, self.current_capacity,
            self.is_start, self.position_queue, self.player_queue,
            self.player_queue_pointer, self.five_cards_of_desk,
            self.current_largest_chips_this_game, self.pool)


class User_Game_play(models.Model):
    user = models.OneToOneField(User_info, on_delete=models.CASCADE)
    position = models.IntegerField(default=10)
    desk = models.ForeignKey(
        Desk_info, on_delete=models.CASCADE,
        null=True)  # a desk can have many users
    user_cards = models.CharField(max_length=30, default='')

    # reset following variables in winner logic
    # -1: fold, 0: have not moved in this round, 1: have moved in this round
    status = models.IntegerField(default=0)
    chips_pay_in_this_game = models.IntegerField(default=0)
    is_fold = models.BooleanField(default=False)

    def __str__(self):
        return "desk_name: %s, username: %s, position: %d, user_cards: %s, status: %d, chips_pay_in_this_game: %d"%\
               (self.desk.desk_name, self.user.user.username, self.position, self.user_cards, self.status, self.chips_pay_in_this_game)


class Game_info(models.Model):
    game_name = models.CharField(max_length=50)
    current_version = models.CharField(max_length=50)
    process_name = models.CharField(max_length=50)
    is_maintain = models.BooleanField()
    max_num_players = models.IntegerField(default=9)
    min_num_players = models.IntegerField(default=2)

    def __str__(self):
        return self.game_name


class Card_info(models.Model):
    color = models.CharField(max_length=20)
    number = models.CharField(max_length=20)
    in_deck = models.BooleanField()
    desk = models.ForeignKey(Desk_info, on_delete=models.CASCADE)
