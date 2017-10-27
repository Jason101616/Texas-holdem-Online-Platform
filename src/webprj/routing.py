from channels.routing import route
from texas.test_consumer import *

channel_routing = [
    route('websocket.receive', ws_echo),
    route('websocket.connect', ws_connect),
]