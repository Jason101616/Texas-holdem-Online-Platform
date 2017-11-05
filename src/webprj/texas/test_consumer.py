from channels import Group
import json
from channels.sessions import channel_session
from urllib.parse import parse_qs
import random

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
        content = {'card': message.channel_session['card'],
                    'status': 'fold',
                   'hold_click_cnt': message.channel_session['hold_click_cnt'],
                   'result': result}
        Group('test').send({'text': json.dumps(content)})

def shuffle_card():
    nums = []
    for i in range(52):
        nums.append(i)
    ans = random.sample(nums, len(nums))[0:9]

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
    return "test"

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
