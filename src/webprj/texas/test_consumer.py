from channels import Group
import json
from channels.sessions import channel_session
from urllib.parse import parse_qs

#demo 2
@channel_session
def ws_msg(message):
    print("in ws_msg", message)
    Group("test").send({
        "text": json.dumps({
            "text": message["text"],
            "username": message.channel_session["username"],
        }),
    })

# Connected to websocket.connect
@channel_session
def ws_add(message):
    print("in ws_add", message)
    # Accept the incoming connection
    message.reply_channel.send({"accept": True})
    message.channel_session['username'] = "test"
    # Add them to the chat group
    Group("test").add(message.reply_channel)


# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("test").discard(message.reply_channel)
