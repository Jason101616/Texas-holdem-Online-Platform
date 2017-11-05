from channels import Group
import json
from channels.sessions import channel_session
from urllib.parse import parse_qs

#demo 1
# def ws_echo(message):
#     print(message.content)
#     message.reply_channel.send({
#         'text': message.content['text'] + ' done!',
#     })
#
# @channel_session
# def ws_connect(message):
#     # Accept connection
#     message.reply_channel.send({"accept": True})
#     # Parse the query string
#     params = parse_qs(message.content["query_string"])
#     if b"username" in params:
#         # Set the username in the session
#         message.channel_session["username"] = params[b"username"][0].decode("utf8")
#         # Add the user to the room_name group
#         Group("test").add(message.reply_channel)
#     else:
#         # Close the connection.
#         message.reply_channel.send({"close": True})


#demo 2
@channel_session
def ws_msg(message):
    print("in ws_msg", message)
    Group("test").send({
        "text": json.dumps({
            "text": message["text"],
            "username": message.channel_session['username'],
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

# Connected to websocket.connect
# def ws_add(message):
#     # Accept the connection
#     print("in ws_add", message)
#     message.reply_channel.send({"accept": True})
#     # Add to the chat group
#     Group("chat").add(message.reply_channel)
#
# # Connected to websocket.receive
# def ws_msg(message):
#     print("in ws_msg", message)
#     Group("chat").send({
#         "text": "[user] %s" % message.content['text'],
#     })
#
# # Connected to websocket.disconnect
# def ws_disconnect(message):
#     Group("chat").discard(message.reply_channel)