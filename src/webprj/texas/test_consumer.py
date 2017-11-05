from channels import Group
import json
from channels.sessions import channel_session
from urllib.parse import parse_qs
import requests

@channel_session
def ws_msg(message):
    # print(message['text'])

    data = json.loads(message['text'])
    print(data)
    if data['message'] == 'click get_card':
        card = get_card()
        message.channel_session['card'] = card
        content = {'card': card}
        Group('test').send({'text': json.dumps(content)})
    elif data['message'] == 'click game_hold':
        print("in click game_hold")
        message.channel_session['hold_click_cnt'] += 1
        content = {'card': message.channel_session['card'],
                   'hold_click_cnt': message.channel_session['hold_click_cnt']}
        Group('test').send({'text': json.dumps(content)})

# TODO finish this shuffle function
def get_card():
    return [1, 2, 3, 4]

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
