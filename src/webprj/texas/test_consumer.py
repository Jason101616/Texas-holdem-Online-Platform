from channels import Group

#demo 1
def ws_echo(message):
    print(message.content)
    message.reply_channel.send({
        'text': message.content['text'] + ' done!',
    })

def ws_connect(message):
    message.reply_channel.send({'accept': True})


#demo 2

def ws_msg(message):
    Group("test").send({
        "text": "[user] %s" % message.content['text'],
    })

# Connected to websocket.connect
def ws_add(message):
    # Accept the incoming connection
    message.reply_channel.send({"accept": True})
    # Add them to the chat group
    Group("test").add(message.reply_channel)

# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("test").discard(message.reply_channel)