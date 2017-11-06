from channels import Group
import json
from channels.sessions import channel_session
from urllib.parse import parse_qs
import random
from . import test_compare

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
        content = {'card': card, 
                'status': 'start',
                'hold_click_cnt': message.channel_session['hold_click_cnt']}
        Group('test').send({'text': json.dumps(content)})

    elif data['message'] == 'click game_hold':
        message.channel_session['hold_click_cnt'] += 1
        if (message.channel_session['hold_click_cnt'] < 3):
            content = {'card': message.channel_session['card'],
                    'status': 'hold',
                   'hold_click_cnt': message.channel_session['hold_click_cnt'],
                   'result': ""}
        else:
            result = decide_winner(message.channel_session['card'])
            content = {'card': message.channel_session['card'],
                    'status': 'hold',
                   'hold_click_cnt': message.channel_session['hold_click_cnt'],
                   'result': result}
        Group('test').send({'text': json.dumps(content)})

    elif data['message'] == 'click game_fold':
        result = "You lose!"
        message.channel_session['hold_click_cnt'] += 1
        message.channel_session['hold_click_cnt'] = 0
        content = {'card': message.channel_session['card'],
                    'status': 'fold',
                   'hold_click_cnt': message.channel_session['hold_click_cnt'],
                   'result': result}
        Group('test').send({'text': json.dumps(content)})


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
    ans = random.sample(nums, len(nums))[0:9]#

    names = []
    for rand in ans:
        color = (int)(rand - rand % 13) / 13
        index = rand - color * 13
        name = []

        if index >=0 and index <= 9:
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

# TODO: finish this function
def decide_winner(card):
    print (card)
    my = test_compare.transfer(card[0:5] + card[7:9])
    robot = test_compare.transfer(card[0:7])
    my_level, my_score, my_type = test_compare.highest(my)
    robot_level, robot_score, robot_type = test_compare.highest(robot)
    if (my_level > robot_level) or my_level == robot_level and my_score > robot_score:
        return my_type + " V.S." + robot_type + "<br> You win!"
    elif my_level == robot_level and my_score == robot_score:
        return my_type + " V.S." + robot_type + "<br> Draw!"
    else:
        return my_type + " V.S." + robot_type + "<br> You lose!"

# Connected to websocket.connect
@channel_session
def ws_add(message):
    # Accept the incoming connection
    message.reply_channel.send({"accept": True})
    message.channel_session['hold_click_cnt'] = 0
    # Add them to the chat group
    Group("test").add(message.reply_channel)


# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("test").discard(message.reply_channel)
