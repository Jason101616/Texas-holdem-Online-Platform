from channels import Group
import json
from channels.sessions import channel_session
import random
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from django.db import transaction

from texas.models import *
from texas.views import *
from . import test_compare, desk_manipulation

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# global public name
public_name = 'desk0'

# an global private group name array for each player
private_group = ['1', '2', '3', '4', '5', '6', '7', '8', '9']


def refresh_desk(desk):
    desk.delete()
    desk = Desk_info(desk_name=public_name)
    desk.save()


@transaction.atomic
@channel_session_user
def diconnect_user(message, username):
    print('disconnect!')
    # Disconnect
    print(username)
    # get desk
    desk = Desk_info.objects.get(desk_name='desk0')
    max_capacity = desk.capacity
    # Group(public_name).discard(message.reply_channel)
    print('success')
    desk.current_capacity += 1

    # decide is_start
    if desk.current_capacity >= desk.capacity - 1:
        desk.is_start = False

    # decide owner
    this_user_info = User_info.objects.get(user=message.user)
    this_player = User_Game_play.objects.get(user=this_user_info)
    if desk.owner == this_user_info:
        players = User_Game_play.objects.filter(desk=desk)
        print(players)
        if len(players) == 1:
            # if this is the last user, desk.owner = None
            desk.owner = None
        else:
            # if still have people in the current desk, give the owner to him
            for player in players:
                if player != this_player:
                    desk.owner = player.user
                    break

    # retrieve position queue
    desk.position_queue += str(this_player.position)
    print("after leave: ", desk)

    # If current player is 1, owner can not start the game
    if desk.current_capacity == max_capacity - 1:
        content = {'can_start': 'no'}
        this_player = User_Game_play.objects.get(user=desk.owner)
        print(this_player.position)
        Group(str(this_player.position)).send({'text': json.dumps(content)})

    # delete User_Game_play
    User_Game_play.objects.get(user=this_user_info).delete()
    Group(desk.desk_name).discard(message.reply_channel)

    desk.save()

    if desk.current_capacity == desk.capacity:
        refresh_desk(desk)
    return


@transaction.atomic
@channel_session_user
def start_logic(message):
    print('start signal received!')
    # TODO: let the lowest position the dealer
    # arrange dealer
    cur_desk = Desk_info.objects.get(desk_name='desk0')
    users_of_cur_desk = User_Game_play.objects.filter(
        desk=cur_desk).order_by('position')
    print(users_of_cur_desk)
    active_users_queue = ''
    for user in users_of_cur_desk:
        active_users_queue += str(user.position)
    cur_desk.player_queue = active_users_queue
    print(active_users_queue)  # test
    # the first person in the queue is initialized as dealer
    dealer = User_Game_play.objects.get(
        desk=cur_desk, position=int(cur_desk.player_queue[0]))
    # TODO: let the next two player be blinds
    # arrange blind
    next_pos_in_queue = get_next_pos(0, len(users_of_cur_desk))
    small_blind = User_Game_play.objects.get(
        desk=cur_desk, position=int(cur_desk.player_queue[next_pos_in_queue]))
    next_pos_in_queue = get_next_pos(next_pos_in_queue, len(users_of_cur_desk))
    big_blind = User_Game_play.objects.get(
        desk=cur_desk, position=int(cur_desk.player_queue[next_pos_in_queue]))
    # the person move next is the next position of big_blind
    cur_desk.player_queue_pointer = get_next_pos(next_pos_in_queue,
                                                 len(users_of_cur_desk))

    # TODO: give every users 2 cards
    # arrange card
    cards = test_compare.shuffle_card(len(users_of_cur_desk))
    # first 5 random cards give desk
    desk_cards = ''
    for card in cards[:5]:
        desk_cards += str(card) + ' '
    desk_cards = desk_cards[:-1]  # delete the last space character
    cur_desk.five_cards_of_desk = desk_cards

    # Group(cur_desk.desk_name).send({'desk_cards': cur_desk.five_cards_of_desk})

    # giver each users his cards and store it in the User_Game_play
    start_index = 5
    for user in users_of_cur_desk:
        cur_user_cards = ''
        for card in cards[start_index:start_index + 2]:
            cur_user_cards += str(card) + ' '
        cur_user_cards = cur_user_cards[:-1]
        start_index += 2
        user.user_cards = cur_user_cards

    for user in users_of_cur_desk:
        user.save()
        print("user after start: ", user)
        content = {'user_cards': user.user_cards}
        Group(str(user.position)).send({'text': json.dumps(content)})

    # tell the public channel, who is dealer, who is big blind, who is small blind
    content = {
        'dealer': [dealer.user.user.username, dealer.position],
        'big_blind': [big_blind.user.user.username, big_blind.position],
        'small_blind': [small_blind.user.user.username, small_blind.position]
    }
    Group(cur_desk.desk_name).send({'text': json.dumps(content)})

    cur_desk.save()

    print("desk after start: ", cur_desk)
    return cur_desk.player_queue[cur_desk.player_queue_pointer]


# player_queue is a cyclic queue, the next pos of the last pos is 0
def get_next_pos(cur_pos, len_queue):
    if cur_pos <= len_queue - 2:
        return cur_pos + 1
    return 0


def give_control(player_position):
    content = {'move': player_position}
    Group(public_name).send({'text': json.dumps(content)})
    return


def find_next_player(desk):
    # update pointer and get next player
    desk.player_queue_pointer = get_next_pos(desk.player_queue_pointer, len(desk.player_queue))
    next_player = User_Game_play.objects.get(desk=desk, position=int(desk.player_queue[desk.player_queue_pointer]))
    desk.player_queue_pointer = get_next_pos(desk.player_queue_pointer, len(desk.player_queue))
    return next_player


def judge_logic(next_player, desk):
    pass

    status = next_player.status
    # TODO: if next player hasn't moved in this turn, give control to him
    if status == 0:
        give_control(next_player.position)

    # TODO: if his status is fold: skip this player
    # find_next_player()
    if status == -1:
        next_player = find_next_player(desk)
        return judge_logic(next_player, desk)

    # TODO: if his stutas is not fold
        # TODO: if his bet is the highest bet in the table
        # go to next phase
        # TODO: if his bet is not the highest bet in the table
        # give_control(next_player)
    if status == 1:
        if next_player.chips_pay_in_this_game == desk.current_largest_chips_this_game:
            return winner_logic(desk)
        else:
            give_control(next_player.position)


def winner_logic(cur_desk):
    pass
    # TODO: if there's only one player whose status is other than fold
        # winner(this_player)
    count_not_fold = 0
    users_of_desk = User_Game_play.objects.filter(
        desk=cur_desk).order_by('position')
    for user in users_of_desk:
        if user.status != -1:
            count_not_fold += 1
        else:
            winner = user
    if count_not_fold == 1:
        pass
        #return assign_winner(user)

    # TODO: if this is the end of river phase
    if cur_desk.phase == 'river':
        pass
        # TODO: compare all players's cards
        #user = compare(users_of_desk)
        #assign_winner(user)

    # TODO: continue the game to next phase
    return next_phase()


def next_phase():
    pass
    # TODO: Server send another public card to the table

    # TODO: Server let next player to move, wait for signal


@transaction.atomic
@channel_session_user
def ws_msg(message):
    # print(message['text'])
    try:
        data = json.loads(message['text'])
    except:
        return
    print(data)

    if 'start_game' in data:
        print('start_game')
        first_player_position = start_logic(message)
        content = {'move': first_player_position}
        Group(public_name).send({'text': json.dumps(content)})
        return

    # The player click leave room
    if 'command' in data:
        if data['command'] == 'leave':
            print(message.user.username)
            diconnect_user(message, message.user.username)
            content = {'test': 'test'}
            Group(public_name).send({'text': json.dumps(content)})
            print('test_msg sent!')
            return

    # get this_user, this_user_info, this_user_game_play, this_desk
    this_user = get_object_or_404(User, username=message.user.username)
    this_user_info = User_info.objects.get(user=this_user)
    this_user_game_play = User_Game_play.objects.get(user=this_user_info)
    this_desk = this_user_game_play.desk
    # set current user status 1: have moved in this round
    this_user_game_play.status = 1
    if data['message'] == 'hold':
        # no need to handle this situation
        pass
    elif data['message'] == 'check':
        # current user put more chips
        this_user_info.chips -= (this_desk.current_largest_chips_this_game -
                                 this_user_game_play.chips_pay_in_this_game)
        this_user_game_play.chips_pay_in_this_game = this_desk.current_largest_chips_this_game

    elif data['message'] == 'fold' or data['message'] == 'timeout':
        # update the queue
        this_desk.player_queue = this_desk.player_queue[:this_desk.player_queue_pointer] + \
                                 this_desk.player_queue[this_desk.player_queue_pointer + 1:]
        this_desk.player_queue_pointer -= 1

    elif data['message'] == 'raise':
        chips_add = data['value']
        # current user put more chips
        this_user_info.chips -= chips_add
        this_user_game_play.chips_pay_in_this_game += chips_add
        this_desk.current_largest_chips_this_game = this_user_game_play.chips_pay_in_this_game

    # find next move person position
    next_pos_queue = get_next_pos(this_desk.player_queue_pointer,
                                  len(this_desk.player_queue))
    this_desk.player_queue_pointer = next_pos_queue
    next_pos_desk = int(this_desk.player_queue[next_pos_queue])
    content = {'next_mov_pos': next_pos_desk}
    # save the modified model, send the public group which user should move the next round
    this_user_info.save()
    this_user_game_play.save()
    this_desk.save()
    Group(public_name).send({'text': json.dumps(content)})
    #judge_logic(next_pos_desk, this_desk.player_queue)


# Connected to websocket.connect
@transaction.atomic
@channel_session_user_from_http
def ws_add(message):
    desk = Desk_info.objects.get(desk_name='desk0')

    # an global private group name array for each player
    private_group = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    # an public group name for all player
    public_name = desk.desk_name

    # max compacity
    max_capacity = desk.capacity

    # list of players
    players = {}

    # test
    # desk.is_start = False
    # desk.save()

    # Add them to the public group
    Group(desk.desk_name).add(message.reply_channel)

    if desk.is_start:
        # Reject the incoming connection
        message.reply_channel.send({"accept": True})
        content = {'is_start': 'yes'}
        Group(public_name).send({'text': json.dumps(content)})
        Group(public_name).discard(message.reply_channel)
        return

    if desk.current_capacity == 0:
        # Reject the incoming connection
        message.reply_channel.send({"accept": True})
        content = {'is_full': 'yes'}
        desk_manipulation.disable_desk(desk)
        Group(public_name).send({'text': json.dumps(content)})
        Group(public_name).discard(message.reply_channel)
        return

    this_user = get_object_or_404(User, username=message.user.username)
    this_user_info = User_info.objects.get(user=this_user)

    this_position = int(desk.position_queue[0])
    desk.position_queue = desk.position_queue[1:]
    print(this_user_info)

    # Allocate a postion to the user
    player = User_Game_play(
        user=this_user_info, desk=desk, position=this_position)
    player.desk = desk
    player.save()

    player = User_Game_play.objects.get(user=this_user_info)
    print("created player")
    print(player)

    if desk.current_capacity == max_capacity:
        desk.owner = this_user_info

    desk.current_capacity -= 1
    print(desk.current_capacity)

    # Accept the incoming connection
    message.reply_channel.send({"accept": True})
    message.channel_session['hold_click_cnt'] = 0

    # Add them to the public group
    Group(public_name).add(message.reply_channel)

    # Add the user to the private group
    position = str(player.position)
    Group(position).add(message.reply_channel)
    Group(position).send({'text': desk.desk_name})

    # Give owner signal
    if desk.owner == this_user_info:
        Group(position).send({'text': 'owner!'})

    player.save()
    desk.save()

    # Boardcast to all player
    content = {
        'new_player': message.user.username,
        'position': player.position
    }
    Group(public_name).send({'text': json.dumps(content)})

    # If current player is 2 or more, owner can start the game
    if desk.current_capacity == max_capacity - 2:
        content = {'can_start': 'yes'}
        this_player = User_Game_play.objects.get(user=desk.owner)
        print(this_player.position)
        Group(str(this_player.position)).send({'text': json.dumps(content)})

    print('c:%d,m:%d,f:%d,o:%s,p:%s' %
          (desk.current_capacity, desk.capacity, desk.is_start, desk.owner,
           player.position))

    print("after enter: ", desk)


# Connected to websocket.disconnect
@transaction.atomic
@channel_session_user_from_http
def ws_disconnect(message):
    print('disconnect!')
    # Disconnect
    # get desk
    # TODO: the desk_name can be dynamic when support multi-desk
    desk = Desk_info.objects.get(desk_name='desk0')
    # print(desk)
    # Group(public_name).discard(message.reply_channel)
    print('success')
    desk.current_capacity += 1

    # decide how to change is_start
    if desk.current_capacity >= desk.capacity - 1:
        desk.is_start = False

    # decide who is the next owner
    this_user_info = User_info.objects.get(user=message.user)
    this_player = User_Game_play.objects.get(user=this_user_info)
    if desk.owner == this_user_info:
        players = User_Game_play.objects.filter(desk=desk)
        # print(players)
        if len(players) == 1:
            # if this is the last user, desk.owner = None
            desk.owner = None
        else:
            # if still have people in the current desk, give the owner to him
            for player in players:
                if player != this_player:
                    desk.owner = player.user
                    break
    desk.save()
    # delete User_Game_play
    User_Game_play.objects.get(user=this_user_info).delete()
    Group(desk.desk_name).discard(message.reply_channel)
    return
