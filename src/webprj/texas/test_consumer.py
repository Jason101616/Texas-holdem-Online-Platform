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
    # let the user in lowest position be the dealer
    cur_desk = Desk_info.objects.get(desk_name='desk0')
    users_of_cur_desk = User_Game_play.objects.filter(
        desk=cur_desk).order_by('position')
    print(users_of_cur_desk)
    active_users_queue = ''
    for user in users_of_cur_desk:
        active_users_queue += str(user.position)
    cur_desk.player_queue = active_users_queue
    print(active_users_queue)  # test
    cur_desk.save()
    # the first person in the queue is initialized as dealer
    dealer = User_Game_play.objects.get(
        desk=cur_desk, position=int(cur_desk.player_queue[0]))

    # let the next two player be blinds
    # next_pos_in_queue = get_next_pos(0, len(users_of_cur_desk))
    next_pos_in_queue = get_next_pos(0, cur_desk.player_queue)
    small_blind = User_Game_play.objects.get(
        desk=cur_desk, position=int(cur_desk.player_queue[next_pos_in_queue]))
    # next_pos_in_queue = get_next_pos(next_pos_in_queue, len(users_of_cur_desk))
    next_pos_in_queue = get_next_pos(next_pos_in_queue, cur_desk.player_queue)
    big_blind = User_Game_play.objects.get(
        desk=cur_desk, position=int(cur_desk.player_queue[next_pos_in_queue]))

    # the person move next is the next position of big_blind
    # cur_desk.player_queue_pointer = get_next_pos(next_pos_in_queue,
    #                                              len(users_of_cur_desk))
    cur_desk.player_queue_pointer = get_next_pos(next_pos_in_queue,
                                                 cur_desk.player_queue)

    # give every users 2 cards
    cards = test_compare.shuffle_card(len(users_of_cur_desk))

    # first 5 random cards give desk
    desk_cards = ''
    for card in cards[:5]:
        desk_cards += str(card) + ' '
    desk_cards = desk_cards[:-1]  # delete the last space character
    cur_desk.five_cards_of_desk = desk_cards

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
# def get_next_pos(cur_pos, len_queue):
#     if cur_pos <= len_queue - 2:
#         return cur_pos + 1
#     return 0

def get_next_pos(cur_pos, player_queue):
    len_queue = len(player_queue)
    for index, char in enumerate(player_queue):
        if cur_pos == int(char):
            pos = index
    if pos == len_queue - 1:
        return 0
    return pos + 1


def give_control(player_position):
    print('give control to player position: ', player_position)
    # TODO: current round biggest chips
    this_desk = Desk_info.objects.get(desk_name=public_name)
    content = {'move': int(player_position) + 1, 'current_round_largest_chips': this_desk.current_round_largest_chips}
    Group(public_name).send({'text': json.dumps(content)})


# def find_next_player(desk):
#     # update pointer and get next player
#     desk.player_queue_pointer = get_next_pos(desk.player_queue_pointer, len(desk.player_queue))
#     next_player = User_Game_play.objects.get(desk=desk, position=int(desk.player_queue[desk.player_queue_pointer]))
#     # desk.player_queue_pointer = get_next_pos(desk.player_queue_pointer, len(desk.player_queue))
#     desk.save()
#     return next_player


def judge_logic(next_player, desk):
    if len(desk.player_queue) == 1:
        print("judge logic b0")
        assign_winner(next_player)
        return

    status = next_player.status
    # if next player hasn't moved in this turn, give control to him
    if status == 0:
        print("judge logic b1")
        give_control(next_player.position)
        return

    # if his status is fold: skip this player
    # find_next_player()
    # if status == -1:
    #     print("judge logic b2")
    #     next_player = find_next_player(desk)
    #     return judge_logic(next_player, desk)

    # if his stutas is not fold
    if status == 1:
        print("judge logic b3")
        # if his bet is the highest bet in the table
        if next_player.chips_pay_in_this_game == desk.current_largest_chips_this_game:
            print("judge logic b31")
            # go to winner_logic
            return winner_logic(desk)
        else:
            # if his bet is not the highest bet in the table
            # give_control(next_player)
            print("judge logic b32")
            give_control(next_player.position)


def assign_winner(winner):
    print("assign winner: ",winner)
    # assign the winner, and show all the cards to all users
    cur_desk_users = User_Game_play.objects.filter(desk=winner.desk)
    all_user_cards = {}
    pools = 0
    for user in cur_desk_users:
        if user != winner:
            pools += user.chips_pay_in_this_game
        all_user_cards[user.position] = user.user_cards
        # reset all users' chips_pay_in_this_game
        user.chips_pay_in_this_game = 0
        # reset status
        user.status = 0
        # reset is_fold
        user.is_fold = False
        if user != winner:
            user.save()

    content = {'winner_pos': winner.position, 'winner': winner.user.user.username, 'cards': all_user_cards}
    Group(public_name).send({'text': json.dumps(content)})
    # reset the phase of the current desk
    winner.desk.phase = 'pre_flop'
    winner.desk.current_largest_chips_this_game = 0
    winner.desk.pool = 0
    winner.desk.current_round_largest_chips = 0
    print('in assign_winner, winner.desk.pool:', winner.desk.pool)
    # winner gain all the chips in current game
    winner.user.chips += pools
    winner.save()
    winner.user.save()
    winner.desk.save()
    print("assign_winner success")


def winner_logic(cur_desk):
    # if there's only one player whose status is other than fold
    if len(cur_desk.player_queue) == 1:
        winner = User_Game_play.objects.get(desk=cur_desk, position=int(cur_desk.player_queue[0]))
        assign_winner(winner)
        return

    # if this is the end of river phase
    if cur_desk.phase == 'river':
        # TODO: modify decide_winner function
        winner_pos, results = river_compare(cur_desk)
        print(winner_pos)
        # for test, just give the first person in the queue
        #TODO: multiple winner logic
        winner = User_Game_play.objects.get(desk=cur_desk, position=winner_pos[0])
        assign_winner(winner)
        return

    # continue the game to next phase
    return next_phase(cur_desk)


def river_compare(cur_desk):
    pass
    cur_cards = cur_desk.five_cards_of_desk
    public_card_list = list(map(int,cur_cards.split(' ')))
    print(public_card_list)
    all_user_card = []
    for i in cur_desk.player_queue:
        user = User_Game_play.objects.get(desk=cur_desk, position=i)
        tmp = (user.position, public_card_list + list(map(int,user.user_cards.split(' '))))
        all_user_card.append(tmp)
    print(all_user_card)
    winner, results = test_compare.decide_winner_all(all_user_card)
    return winner, results


def next_phase(cur_desk):
    print("next_phase")
    if cur_desk.phase == 'pre_flop':
        # show all users the first three cards of the desk
        cur_desk.phase = 'flop'
        cur_cards = cur_desk.five_cards_of_desk
        card_list = cur_cards.split(' ')
        for i in range(len(card_list)):
            card_list[i] = int(card_list[i])
        content = {'desk_cards': card_list[:3]}

    elif cur_desk.phase == 'flop':
        # show all users the first four cards of the desk
        cur_desk.phase = 'turn'
        cur_cards = cur_desk.five_cards_of_desk
        card_list = cur_cards.split(' ')
        for i in range(len(card_list)):
            card_list[i] = int(card_list[i])
        content = {'desk_cards': card_list[:4]}

    elif cur_desk.phase == 'turn':
        # show all users the first five cards of the desk
        cur_desk.phase = 'river'
        cur_cards = cur_desk.five_cards_of_desk
        card_list = cur_cards.split(' ')
        for i in range(len(card_list)):
            card_list[i] = int(card_list[i])
        content = {'desk_cards': card_list}

    Group(public_name).send({'text': json.dumps(content)})

    # let the player next to the dealer to move
    first_user = 0
    for i in cur_desk.player_queue:
        user = User_Game_play.objects.get(desk=cur_desk,position=i)
        if user.status != -1:
            user.status = 0
            user.save()
            if first_user == 0:
                first_user = 1
                continue
            if first_user == 1:
                first_user = 2
                next_user = user
    cur_desk.current_round_largest_chips = 0
    cur_desk.save()
    give_control(next_user.position)


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
        cur_desk = Desk_info.objects.get(desk_name='desk0')
        User_Game_play.objects.get(desk=cur_desk, position=first_player_position).status = 1
        # '+1' added by lsn
        content = {'move': int(first_player_position) + 1, 'current_round_largest_chips': cur_desk.current_round_largest_chips}
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

    if data['message'] == 'call' or data['message'] == 'check' or data['message'] == 'hold':
        # current user put more chips
        this_user_info.chips -= (this_desk.current_largest_chips_this_game -
                                 this_user_game_play.chips_pay_in_this_game)
        this_user_game_play.chips_pay_in_this_game = this_desk.current_largest_chips_this_game
        this_desk.pool += (this_desk.current_largest_chips_this_game -
                           this_user_game_play.chips_pay_in_this_game)
        this_user_game_play.status = 1


    elif data['message'] == 'fold' or data['message'] == 'timeout':
        # update the queue
        this_desk.player_queue = this_desk.player_queue[:this_desk.player_queue_pointer] + \
                                 this_desk.player_queue[this_desk.player_queue_pointer + 1:]
        this_desk.player_queue_pointer -= 1
        this_user_game_play.status = 1

    elif data['message'] == 'raise':
        chips_add = data['value']
        # current user put more chips
        this_user_info.chips -= chips_add
        this_user_game_play.chips_pay_in_this_game += chips_add
        this_desk.current_largest_chips_this_game = this_user_game_play.chips_pay_in_this_game
        this_desk.pool += chips_add
        if chips_add < this_desk.current_round_largest_chips:
            print("chips_add < this_desk.current_round_largest_chips")
            exit(0)
        this_desk.current_round_largest_chips = data['value']
        this_user_game_play.status = 1
    this_user_game_play.save()
    # find next move person position
    # next_pos_queue = get_next_pos(this_desk.player_queue_pointer,
    #                                len(this_desk.player_queue))
    next_pos_queue = get_next_pos(this_user_game_play.position, this_desk.player_queue)


    this_desk.player_queue_pointer = next_pos_queue
    next_pos_desk = int(this_desk.player_queue[next_pos_queue])
    print('next_pos_desk: ', next_pos_desk)
    next_user = User_Game_play.objects.get(desk=this_desk,position=next_pos_desk)

    content = {'cur_user_pos': this_user_game_play.position, 'cur_user_chips': this_user_info.chips,
               'total_chips_current_game': this_desk.pool}
    print(content)
    Group(public_name).send({'text': json.dumps(content)})

    # save the modified model, send the public group which user should move the next round
    this_user_info.save()
    this_user_game_play.save()
    this_desk.save()
    print ("next_user before judge logic: ", next_user)
    judge_logic(next_user, this_desk)


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
    #print(this_user_info)

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
    if desk.current_capacity <= max_capacity - 2:
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
