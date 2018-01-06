from channels.routing import route
from texas.test_consumer import *

channel_routing = [
    route('websocket.receive', ws_msg),
    route('websocket.connect', ws_add),
    route('websocket.disconnect',ws_disconnect),
]