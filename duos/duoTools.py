#coding:utf-8

from django.db import models
from .models import Account,Application

import base64
import random
import hashlib
import hmac
import time

DUO_PREFIX = 'TX'
AUTH_PREFIX = 'AUTH'
EXPIRETIME = 60



class DuoFormatException(Exception):
    pass

def parseDuoSig(sig):
    '''
    拆分sig，返回{'prefix':prefix,
    'content':(username,iKey,expiretime),
    'sha_1':加密信息}
    并检查格式，若格式错误则返回抛出异常
    '''
    s = sig.split('|')
    if len(s)!=3:
        raise DuoFormatException()
    prefix,cookie,sha_1 = s
    try:
        #将cookie解码后转换为Unicode
        import chardet
        s = [c.decode(chardet.detect(c)['encoding'])  \
            for c in base64.b64decode(cookie).split('|')]

    except TypeError,e:
        raise DuoFormatException()
    if len(s) != 3:
        raise DuoFormatException()
    userName,iKey,expiretime = s
    print 'inParseDuoSig %s' %(iKey)
    ret =  {
        'prefix':prefix,
        'content':s,
        'sha_1':sha_1
    }
    return ret

def _hmac_sha1(key, msg):
    ctx = hmac.new(key, msg, hashlib.sha1)
    return ctx.hexdigest()


def validateParams(sigDicts,iKey,sKey):
    '''
    验证前缀，Ikey是否合法，验证加密信息是否正确加密
    '''
    if DUO_PREFIX != sigDicts['prefix'] or iKey != sigDicts['content'][1]:
        return False
    cookie = '%s|%s' %(DUO_PREFIX,base64.b64encode('|'.join(sigDicts['content'])))
    newSig = _hmac_sha1(sKey.encode('utf-8'),cookie)
    if _hmac_sha1(sKey.encode('utf-8'),newSig) != _hmac_sha1(sKey.encode('utf-8'),sigDicts['sha_1']):
        return False
    return True

def checkUserEnrolled(userName,application):
    '''
    验证user是否已经enroll，若是返回user，否则返回None
    '''
    users = application.user_set.filter(user_name=userName)
    if len(users) == 0:
        return None
    return users[0]


def signResponse(sigDicts,sKey):
    '''
    返回response的参数值，更新expiretime,prefix
    '''
    sigDicts['content'][-1] = str(int(time.time()) + EXPIRETIME)
    cookie = '%s|%s' % (AUTH_PREFIX,base64.b64encode('|'.join(sigDicts['content'])))
    newSig = _hmac_sha1(sKey.encode('utf-8'),cookie)
    return '%s|%s' %(cookie,newSig)


def getIp(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ip =  request.META['HTTP_X_FORWARDED_FOR']  
    else:  
        ip = request.META['REMOTE_ADDR']  
    return ip





    


    
    