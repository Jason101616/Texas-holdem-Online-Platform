from channels.routing import route

channel_routing = [
    route('websocket.receive','texas.test_consumer.ws_echo')
]