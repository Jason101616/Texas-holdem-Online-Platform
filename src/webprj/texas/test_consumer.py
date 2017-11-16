from channels import Group
import json
from channels.sessions import channel_session
import random
from . import test_compare
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from django.db import transaction
from texas.models import *
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

# an global private group name array for each player
private_group = ['1','2','3','4','5','6','7','8','9']

# an public group name for all player
public_name = 'test'

# max compacity
max_compacity = 9

# current compacity
current_compacity = max_compacity

# start flag of this playroom
start_flag = False

# owner of the playroom
owner = ''

# list of players
players = {}

@channel_session
def ws_msg(message):
    # print(message['text'])

    try:
        data = json.loads(message['text'])
    except:
        return
    print(data)
    if data['message'] == 'click get_card':
        card = shuffle_card()
        message.channel_session['card'] = card
        message.channel_session['hold_click_cnt'] = 0
        content = {
            'card': card,
            'status': 'start',
            'hold_click_cnt': message.channel_session['hold_click_cnt']
        }
        Group(public_name).send({'text': json.dumps(content)})

    elif data['message'] == 'click game_hold':
        message.channel_session['hold_click_cnt'] += 1
        if (message.channel_session['hold_click_cnt'] < 3):
            content = {
                'card': message.channel_session['card'],
                'status': 'hold',
                'hold_click_cnt': message.channel_session['hold_click_cnt'],
                'result': ""
            }
        else:
            result = decide_winner(message.channel_session['card'])
            content = {
                'card': message.channel_session['card'],
                'status': 'hold',
                'hold_click_cnt': message.channel_session['hold_click_cnt'],
                'result': result
            }
        Group(public_name).send({'text': json.dumps(content)})

    elif data['message'] == 'click game_fold':
        result = "You lose!"
        message.channel_session['hold_click_cnt'] += 1
        message.channel_session['hold_click_cnt'] = 0
        content = {
            'card': message.channel_session['card'],
            'status': 'fold',
            'hold_click_cnt': message.channel_session['hold_click_cnt'],
            'result': result
        }
        Group(public_name).send({'text': json.dumps(content)})


"""
output value:
    names = [[num_1,color_1],[num_2,color_2],...[]]
    card = '1',...,'10','J','Q','K'
    color = 0,1,2,3
"""


def shuffle_card():
    nums = []
    for i in range(52):
        nums.append(i)
    ans = random.sample(nums, len(nums))[0:9]  #

    names = []
    for rand in ans:
        color = (int)(rand - rand % 13) / 13
        index = rand - color * 13
        name = []

        if index >= 0 and index <= 9:
            name.append(str(int(index + 1)))
        elif index == 10:
            name.append('J')
        elif index == 11:
            name.append('Q')
        elif index == 12:
            name.append('K')

        name.append(color)
        names.append(name)

    return names


"""
input:
    card: [[Num, Color], ...,]
    card[0-4]: public card
    card[5-6]: robot card
    card[7-8]: my card
return:
    "You win!"
    "You lose!"
"""

def decide_winner(card):
    print(card)
    my = test_compare.transfer(card[0:5] + card[7:9])
    robot = test_compare.transfer(card[0:7])
    my_level, my_score, my_type, my_card = test_compare.highest(my)
    robot_level, robot_score, robot_type, robot_card = test_compare.highest(
        robot)
    if (my_level >
            robot_level) or my_level == robot_level and my_score > robot_score:
        return my_type + " V.S." + robot_type + "<br> You win!"
    elif my_level == robot_level and my_score == robot_score:
        return my_type + " V.S." + robot_type + "<br> Draw!"
    else:
        return my_type + " V.S." + robot_type + "<br> You lose!"


# Connected to websocket.connect
@transaction.atomic
@channel_session_user_from_http
def ws_add(message):
    desk = Desk_info.objects.get(desk_name='desk0')
    this_user = get_object_or_404(User, username=message.user.username)
    this_user_info = User_info.objects.get(user=this_user)
    print (this_user_info)
    #User_Game_play.objects.get(user=this_user_info)
    print (player)
    # an global private group name array for each player
    private_group = ['1','2','3','4','5','6','7','8','9']

    # an public group name for all player
    public_name = desk.desk_name

    # max compacity
    max_capacity = desk.capacity

    # current compacity
    current_capacity = desk.current_capacity

    # start flag of this playroom
    start_flag = False

    # owner of the playroom
    owner = desk.owner

    # list of players
    players = {}

    desk_name = desk.desk_name

    #test
    #desk.is_start = False
    #desk.save()

    # Add them to the public group
    Group(desk_name).add(message.reply_channel)

    if desk.is_start:
        # Reject the incoming connection
        message.reply_channel.send({"accept" : True})
        content = {'is_start' : 'yes'}
        Group(public_name).send({'text' : json.dumps(content)})
        return


    if current_capacity == 0:
        # Reject the incoming connection
        message.reply_channel.send({"accept": True})
        content = {'is_full':'yes'}
        Group(public_name).send({'text': json.dumps(content)})
        return

    if current_capacity == max_capacity:
        owner = message.user.username
        desk.owner = message.user

    current_capacity -= 1

    # Accept the incoming connection
    message.reply_channel.send({"accept": True})
    message.channel_session['hold_click_cnt'] = 0

    # Add them to the public group
    Group(public_name).add(message.reply_channel)

    # Allocate a postion to the user
    player.postion = max_capacity - current_capacity
    position = str(player.position)

    # Add the user to the private group
    Group(position).add(message.reply_channel)
    Group(position).send({'text':desk.desk_name})

    # Give owner signal
    if owner == message.user.username:
        Group(position).send({'text':'owner!'})

    # Boardcast to all player
    content = {'new_player':message.user.username}
    Group(public_name).send({'text': json.dumps(content)})

    desk.save()
    player.save()

    print ('c:%d,m:%d,f:%d,o:%s,p:%s'%(desk.current_capacity, desk.capacity, desk.is_start, desk.owner.username, player.position))



# Connected to websocket.disconnect
@channel_session_user_from_http
def ws_disconnect(message):
    # Disconnect
    desk = Desk_info.objects.get(desk_name='desk0')
    # if full
    if desk.current_capacity == 0:
        Group('desk0').discard(message.reply_channel)
        return
    # if quit game
    desk.current_capacity += 1
    # decide is_start
    if desk.current_capacity >= desk.capacity - 1:
        desk.is_start = False
    # decide owner
    if desk.owner == message.user.User_info:
        players = desk.user_Game_play_set.all()
        if len(players) == 1:
            # if this is the last user, desk.owner = None
            desk.owner = None
        else:
            # if still have people in the current desk, give the owner to him
            for player in players:
                if player != message.user.User_info.User_Game_play:
                    desk.owner = player.User_info
                    break
    # delete User_Game_play
    User_Game_play.objects.get(user=message.user).delete()
    Group(public_name).discard(message.reply_channel)
