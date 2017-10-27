def ws_echo(message):
    message.reply_channel.send({
        'text': message.content['text'],
    })


def ws_connect(message):
    message.reply_channel.send({'accept': True})
