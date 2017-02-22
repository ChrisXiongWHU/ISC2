#coding:utf-8
from channels import Group
from channels.asgi import get_channel_layer
from channels.sessions import channel_session
from django.core.cache import cache
from auth import auth
import json


def auth_connect(message,phone):
    message.reply_channel.send({'accept':True})
    Group("phone-%s" %phone).add(message.reply_channel)

def auth_message(message,phone):
    content = json.loads(message.content['text'])
    if content['cd'] == 'auth':   
        #进行认证操作
        status = auth(phone,content['mobile'])
        if status is True:
            cache.set('%s_auth_status'% phone,True,30)
        else:
            cache.set('%s_auth_status'% phone,False,30)

def auth_disconnect(message,phone):
    Group("phone-%s" %phone).discard(message.reply_channel)

        
        