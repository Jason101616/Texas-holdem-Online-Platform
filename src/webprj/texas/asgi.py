import os, sys
from channels.asgi import get_channel_layer

path = '/home/ubuntu/Team319/src/webprj'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webprj.settings")

channel_layer = get_channel_layer()
