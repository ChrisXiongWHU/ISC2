from channels import route

from .consumers import auth_connect
from .consumers import auth_message
from .consumers import auth_disconnect


mychannel_routing = [
    route("websocket.connect",auth_connect,path=r'^/(?P<phone>[0-9]{11})$'),
    route("websocket.receive",auth_message,path=r'^/(?P<phone>[0-9]{11})$'),
    route("websocket.disconnect",auth_disconnect,path=r'^/(?P<phone>[0-9]{11})$'),
]